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
 * Browser-side parser: fetches the krooster page for `username`, extracts
 * character IDs from __NEXT_DATA__ JSON, and returns the subset of provided
 * `names` whose IDs are present in the roster.
 */
export async function fetchKroosterBrowser(
  username: string,
  chars: Array<{ id: string; name: string }>,
): Promise<string[]> {
  const url = `https://www.krooster.com/u/${encodeURIComponent(username)}`;
  const res = await fetch(url, { headers: { 'User-Agent': 'ak-chars-browser/1.0' } });
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  const html = await res.text();

  // Extract character IDs from __NEXT_DATA__ JSON
  const rosterIds = extractRosterIds(html);

  if (rosterIds.length === 0) {
    // Fallback to old name-based parsing for test cases
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

      console.log(`Krooster: matched ${matched.length} of ${chars.length} names (fallback)`);
      return matched;
    }

    // Final fallback: text content search
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

    console.log(`Krooster: matched ${matched.length} of ${chars.length} names (text fallback)`);
    return matched;
  }

  // Use ID-based matching (primary method)
  const rosterIdSet = new Set(rosterIds);
  const matched = chars.filter((char) => rosterIdSet.has(char.id)).map((char) => char.name);

  console.log(`Krooster: matched ${matched.length} of ${chars.length} characters by ID`);
  console.log('[Krooster Debug] Roster IDs count:', rosterIds.length);
  console.log('[Krooster Debug] First 10 IDs:', rosterIds.slice(0, 10));

  return matched;
}
