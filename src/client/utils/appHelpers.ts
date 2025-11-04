import { Char } from '../../types';
import { getTierSortValue, isTierEqualOrHigher } from './tierUtils';
import { uniqueStrings } from './groupHelpers';

export function getRarities(chars: Char[]) {
  return (uniqueStrings(chars.map((c) => c.rarity)) as string[]).sort(
    (a, b) => Number(b.replace(/\D/g, '')) - Number(a.replace(/\D/g, '')),
  );
}

export function getProfessions(chars: Char[]) {
  return (uniqueStrings(chars.map((c) => c.profession)) as string[]).sort();
}

export function getTiersList(tiers: Record<string, string>) {
  return (uniqueStrings(Object.values(tiers)) as string[]).sort(
    (a, b) => getTierSortValue(b) - getTierSortValue(a),
  );
}

export function filterChars(
  chars: Char[],
  rarity: string,
  profession: string,
  tierFilter: string,
  tiers: Record<string, string>,
  search?: string,
) {
  const searchNorm = (search || '').trim().toLowerCase();
  return chars.filter((c) => {
    if (rarity && c.rarity !== rarity) return false;
    if (profession && profession !== 'All' && c.profession !== profession) return false;
    const t = tiers[c.name || ''] || '';
    if (tierFilter) {
      if (!t) return false;
      if (!isTierEqualOrHigher(t, tierFilter)) return false;
    }
    if (searchNorm) {
      const name = (c.name || '').toLowerCase();
      if (!name.includes(searchNorm)) return false;
    }
    return true;
  });
}

export function sortByTier(chars: Char[], tiers: Record<string, string>) {
  return chars.slice().sort((a, b) => {
    const tierA = tiers[a.name || ''] || '';
    const tierB = tiers[b.name || ''] || '';
    const valA = tierA ? getTierSortValue(tierA) : -999;
    const valB = tierB ? getTierSortValue(tierB) : -999;
    return valB - valA;
  });
}
