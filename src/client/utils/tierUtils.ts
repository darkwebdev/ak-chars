import type { Char } from '../../types';

export const baseOrder = ['F', 'E', 'D', 'C', 'B', 'A', 'S'];

export function getTierSortValue(tier: string): number {
  if (!tier) return -100;
  if (tier === 'EX') return 100;
  const match = tier.match(/^([A-Z]+)([+-])?$/);
  if (!match) return -100;
  const base = match[1];
  const mod = match[2] || '';
  let value = baseOrder.indexOf(base) * 10;
  if (mod === '+') value += 2;
  if (mod === '-') value -= 2;
  return value;
}

export function isTierEqualOrHigher(charTier: string, minTier: string): boolean {
  if (!charTier || !minTier) return true;
  const charValue = getTierSortValue(charTier);
  const minValue = getTierSortValue(minTier);
  return charValue >= minValue;
}

export function highestTierValue(arr: Char[], tiers: Record<string, string>) {
  const vals = arr
    .map((ch) => {
      const t = tiers[ch.name || ''] || '';
      if (!t) return null;
      const match = t.match(/^([A-Z]+)/);
      const base = match ? match[1] : '';
      if (base === 'F') return null;
      return getTierSortValue(t);
    })
    .filter((v): v is number => v !== null && v !== -999);
  if (vals.length === 0) return -999;
  return Math.max(...vals);
}

export function sortGroupKeys(groups: Record<string, Char[]>, tiers: Record<string, string>) {
  return Object.keys(groups).sort((a, b) => {
    if (a === 'Other') return 1;
    if (b === 'Other') return -1;
    const aMax = highestTierValue(groups[a], tiers);
    const bMax = highestTierValue(groups[b], tiers);
    if (bMax !== aMax) return bMax - aMax;
    return a.localeCompare(b);
  });
}
