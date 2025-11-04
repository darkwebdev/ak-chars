import type { Char } from '../../types';
import { highestTierValue } from './tierUtils';

type GroupMeta = {
  key: string;
  chars: Char[];
  total: number;
  ownedCount: number;
  maxTierValue: number;
};

export function uniqueStrings(arr: Array<string | undefined | null>) {
  const out: string[] = [];
  for (const v of arr) {
    if (!v) continue;
    if (!out.includes(v)) out.push(v);
  }
  return out;
}

export function buildGroups(chars: Char[]) {
  return chars.reduce((acc: Record<string, Char[]>, ch) => {
    const key = ch.subProfessionId || 'Other';
    if (!acc[key]) acc[key] = [];
    acc[key].push(ch);
    return acc;
  }, {} as Record<string, Char[]>);
}

export function buildGroupsByKey(chars: Char[], keyFn: (ch: Char) => string) {
  return chars.reduce((acc: Record<string, Char[]>, ch) => {
    const key = keyFn(ch) || 'Other';
    if (!acc[key]) acc[key] = [];
    acc[key].push(ch);
    return acc;
  }, {} as Record<string, Char[]>);
}

export function groupsWithMeta(chars: Char[], tiers: Record<string, string>, ownedIds: string[]) {
  const groups = buildGroups(chars);
  const out: GroupMeta[] = Object.keys(groups).map((k) => {
    const arr = groups[k];
    const total = arr.length;
    const ownedCount = arr.filter((c) => ownedIds.includes(c.id)).length;
    const maxTierValue = highestTierValue(arr, tiers);
    return { key: k, chars: arr, total, ownedCount, maxTierValue };
  });

  out.sort((a, b) => {
    if (a.key === 'Other') return 1;
    if (b.key === 'Other') return -1;
    if (b.maxTierValue !== a.maxTierValue) return b.maxTierValue - a.maxTierValue;
    return a.key.localeCompare(b.key);
  });

  return out;
}

export type { GroupMeta };
