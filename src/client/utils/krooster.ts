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

function removeHidden(html: string) {
  // Use DOM parsing in browser context.
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  // remove elements with class hidden or unowned
  doc.querySelectorAll('.hidden, .unowned').forEach((el) => el.remove());
  return doc.body ? doc.body.textContent || '' : '';
}

/**
 * Browser-side parser: fetches the krooster page for `username`, removes
 * elements with class 'hidden' or 'unowned', normalizes text, and returns
 * the subset of provided `names` that appear in the visible text.
 */
export async function fetchKroosterBrowser(username: string, names: string[]): Promise<string[]> {
  const url = `https://www.krooster.com/u/${encodeURIComponent(username)}`;
  const res = await fetch(url, { headers: { 'User-Agent': 'ak-chars-browser/1.0' } });
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  const html = await res.text();
  const visibleText = removeHidden(html);
  const normPage = normalize(visibleText);

  const matched: string[] = [];
  const seen = new Set<string>();
  for (const n of names) {
    const norm = normalize(n as string);
    if (norm && normPage.includes(norm) && !seen.has(n as string)) {
      seen.add(n as string);
      matched.push(n as string);
    }
  }
  return matched;
}
