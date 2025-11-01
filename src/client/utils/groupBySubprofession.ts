import type { Char } from '../../types';

export function groupBySubprofession(chars: Char[]) {
  return chars.reduce((acc: Record<string, Char[]>, ch) => {
    const key = ch.subProfessionId || 'Other';
    if (!acc[key]) acc[key] = [];
    acc[key].push(ch);
    return acc;
  }, {} as Record<string, Char[]>);
}
