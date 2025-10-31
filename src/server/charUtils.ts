import type { RawChar, Char } from '../types';

export function transformCharacterTable(obj: Record<string, RawChar>): Char[] {
  const entries = Object.entries(obj ?? {}) as [string, RawChar][];
  return entries
    .filter(([k, c]) => k.startsWith('char_') && c.isNotObtainable !== true)
    .map(([k, c]) => {
      let name: string | null = null;
      let rarity: string | null = null;
      let profession: string | null = null;
      let subProfessionId: string | null = null;

      if (c && typeof c === 'object') {
        if ('name' in c && typeof c.name === 'string') name = c.name;
        else if ('appellation' in c && typeof c.appellation === 'string') name = c.appellation;
        if ('rarity' in c && c.rarity != null) rarity = String(c.rarity);
        if ('profession' in c && typeof c.profession === 'string') profession = c.profession;
        if ('subProfessionId' in c && typeof c.subProfessionId === 'string')
          subProfessionId = c.subProfessionId;
      }

      return { id: k, name, rarity, profession, subProfessionId };
    });
}
