import { transformCharacterTable } from './charUtils';
import type { RawChar, Char } from '../types';

const urlEn =
  'https://raw.githubusercontent.com/ArknightsAssets/ArknightsGameData/master/en/gamedata/excel/character_table.json';
const urlCn =
  'https://raw.githubusercontent.com/ArknightsAssets/ArknightsGameData/master/cn/gamedata/excel/character_table.json';

export async function fetchChars(): Promise<Char[]> {
  // Fetch English character table first
  const resEn = await fetch(urlEn);
  if (!resEn.ok) throw new Error(`Failed to fetch chars (EN): ${resEn.status} ${resEn.statusText}`);
  const objEn = (await resEn.json()) as unknown as Record<string, RawChar>;
  const chars = transformCharacterTable(objEn);

  // Fetch Chinese character table to supplement missing entries
  try {
    const resCn = await fetch(urlCn);
    if (resCn.ok) {
      const objCn = (await resCn.json()) as unknown as Record<string, RawChar>;
      const charsCn = transformCharacterTable(objCn);

      // Build set of existing ids from EN
      const existing = new Set(chars.map((c) => c.id));

      // Append chars present in CN but missing in EN.
      for (const c of charsCn) {
        if (!existing.has(c.id)) {
          const entry: Partial<Char> & Record<string, unknown> = { ...c };
          // Prefer the raw CN `appellation` (if present) for name,
          // otherwise fall back to the transformed `name`.
          const raw = (objCn && typeof objCn === 'object' && (objCn as any)[c.id]) || null;
          if (
            raw &&
            typeof raw === 'object' &&
            'appellation' in (raw as any) &&
            typeof (raw as any).appellation === 'string'
          ) {
            entry.name = (raw as any).appellation;
          } else if ((c as any).name) {
            entry.name = (c as any).name;
          }
          console.log(`Appending CN-only char: [${entry.id}] ${entry.name}`);
          chars.push(entry as any);
        }
      }
    }
  } catch (e) {
    // If CN fetch fails, continue with EN-only data
    // (don't throw - supplemental data is optional)
  }

  // Return the transformed chars array. Writing to disk is the responsibility of callers.
  return chars;
}
