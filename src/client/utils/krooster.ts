export function normalize(s: string) {
  return (
    s
      .toString()
      .normalize('NFKD')
      .replace(/['"“”‘’`]/g, '')
      // remove punctuation & symbols excluding letters, numbers and spaces
      .replace(/[\p{P}\p{S}]+/gu, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase()
  );
}

function extractRosterIds(html: string): string[] {
  const scriptMatch = html.match(
    /<script id="__NEXT_DATA__" type="application\/json">(.*?)<\/script>/s,
  );
  if (!scriptMatch) return [];

  try {
    const data = JSON.parse(scriptMatch[1]);
    const roster = data?.props?.pageProps?.data?.roster;
    if (!roster || typeof roster !== 'object') return [];

    return Object.keys(roster);
  } catch (e) {
    console.error('[Krooster] Failed to parse __NEXT_DATA__:', e);
    return [];
  }
}

function removeHidden(html: string) {
  // Use DOM parsing in browser context.
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  // remove elements with class hidden or unowned
  doc.querySelectorAll('.hidden, .unowned').forEach((el) => el.remove());
  return doc;
}

function extractCharacterNames(doc: Document): string[] {
  const names: string[] = [];

  // Find all character name containers (css-rl7vtn is the container for names)
  const nameContainers = doc.querySelectorAll('.css-rl7vtn');

  for (let i = 0; i < nameContainers.length; i++) {
    const container = nameContainers[i];
    const divs = container.querySelectorAll('div');
    if (divs.length === 2) {
      // Alter character: two divs (subtitle + name)
      const subtitle = divs[0].textContent?.trim() || '';
      const name = divs[1].textContent?.trim() || '';
      if (subtitle && name) {
        names.push(`${subtitle} ${name}`);
      }
    } else if (divs.length === 1) {
      // Base character: single div
      const name = divs[0].textContent?.trim() || '';
      if (name) {
        names.push(name);
      }
    }
  }

  return names;
}

function generateNameVariants(name: string): string[] {
  const variants = [name];

  // Handle "X the Y" alter format
  // Krooster shows these as two separate divs: "Y" in one, "X" in another
  // So "Texas the Omertosa" appears as "Omertosa" + "Texas" separately
  const thePattern = /^(.+?)\s+the\s+(.+)$/i;
  const match = name.match(thePattern);
  if (match) {
    const [, first, second] = match;
    // Don't add full reversed format, instead we'll check for both parts separately
    // The normalize function will combine them in the text anyway
    // But we need to ensure both "second" and "first" appear
    variants.push(`${second} ${first}`);
  }

  return variants;
}

/**
 * Parse a Krooster page HTML string and return matched character names from
 * the provided chars list. This can be used when the browser cannot fetch the
 * Krooster page due to CORS — users can paste the page HTML and we parse it
 * locally.
 */
export function parseKroosterHtml(
  html: string,
  chars: Array<{ id: string; name: string }>,
): string[] {
  // Extract character IDs from __NEXT_DATA__ JSON
  const rosterIds = extractRosterIds(html);

  if (rosterIds.length === 0) {
    const doc = removeHidden(html);
    const kroosterNames = extractCharacterNames(doc);

    if (kroosterNames.length > 0) {
      const normalizedKroosterNames = kroosterNames.map((n) => normalize(n));
      const matched: string[] = [];

      for (const char of chars) {
        const variants = generateNameVariants(char.name);
        for (const variant of variants) {
          if (normalizedKroosterNames.includes(normalize(variant))) {
            matched.push(char.name);
            break;
          }
        }
      }

      return matched;
    }

    const textContent = doc.body?.textContent || '';
    const normPage = normalize(textContent);
    const matched: string[] = [];

    for (const char of chars) {
      const variants = generateNameVariants(char.name);
      for (const variant of variants) {
        if (normPage.includes(normalize(variant))) {
          matched.push(char.name);
          break;
        }
      }
    }

    return matched;
  }

  const rosterIdSet = new Set(rosterIds);
  return chars.filter((char) => rosterIdSet.has(char.id)).map((char) => char.name);
}

/**
 * Browser-side parser: fetches the krooster page for `username`, extracts
 * character IDs from __NEXT_DATA__ JSON, and returns the subset of provided
 * `names` whose IDs are present in the roster.
 */
export async function fetchKroosterBrowser(
  username: string,
  chars: Array<{ id: string; name: string }>,
  // Optional proxy string. If provided, the krooster URL will be embedded into
  // the proxy. If the proxy contains the substring "{url}" it will be
  // replaced with encodeURIComponent(kroosterUrl). Otherwise the encoded URL
  // will be appended to the proxy string.
  proxy?: string,
): Promise<string[]> {
  const url = `https://www.krooster.com/network/lookup/${encodeURIComponent(username)}`;
  // Build ordered list of proxies to try. If the caller supplied a proxy (from
  // the UI), try it first, then fall back to built-in proxies.
  const builtInProxies = [
    'https://api.allorigins.win/raw?url=',
    'https://api.allorigins.cf/raw?url=',
    'https://thingproxy.freeboard.io/fetch/',
  ];

  const proxiesToTry: string[] = [];
  if (proxy && proxy.trim()) proxiesToTry.push(proxy.trim());
  for (const p of builtInProxies) {
    if (!proxiesToTry.includes(p)) proxiesToTry.push(p);
  }

  // Shuffle proxiesToTry so we pick a random order each run. This uses a
  // Fisher-Yates shuffle in-place.
  for (let i = proxiesToTry.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = proxiesToTry[i];
    proxiesToTry[i] = proxiesToTry[j];
    proxiesToTry[j] = tmp;
  }

  // Helper to turn a proxy prefix/template into a final fetch URL for target
  const buildFetchUrl = (proxyPrefix: string, target: string) => {
    if (!proxyPrefix) return target;
    if (proxyPrefix.includes('{url}'))
      return proxyPrefix.replace('{url}', encodeURIComponent(target));
    return proxyPrefix + encodeURIComponent(target);
  };

  let lastErr: unknown = null;
  // Try proxies in randomized order. If none succeed, try direct fetch as a last resort.
  const trySequence = [...proxiesToTry, ''];
  for (const p of trySequence) {
    const fetchUrl = p ? buildFetchUrl(p, url) : url;
    try {
      console.log(`[Krooster] attempting fetch via: ${fetchUrl}`);
      const res = await fetch(fetchUrl, { headers: { 'User-Agent': 'ak-chars-browser/1.0' } });
      if (!res.ok) {
        // Treat non-2xx responses as failures and continue to next proxy
        console.warn(`[Krooster] fetch failed ${fetchUrl}: ${res.status}`);
        lastErr = new Error(`Failed to fetch ${fetchUrl}: ${res.status}`);
        continue;
      }
      const html = await res.text();
      const parsed = parseKroosterHtml(html, chars);
      console.log(`[Krooster] matched ${parsed.length} of ${chars.length} characters`);
      return parsed;
    } catch (e: unknown) {
      // Network/CORS error — remember and continue to next proxy
      console.warn(`[Krooster] fetch error for ${fetchUrl}:`, e);
      lastErr = e;
      continue;
    }
  }

  // If we reach here all attempts failed
  const msg = lastErr instanceof Error ? lastErr.message : String(lastErr);
  if (
    msg === 'TypeError: Failed to fetch' ||
    msg.includes('NetworkError') ||
    msg.includes('Failed to fetch')
  ) {
    throw new Error(
      'Unable to fetch Krooster page (network/CORS). Tried multiple proxies; consider supplying a different proxy or running a server-side proxy.',
    );
  }
  throw lastErr;
}
