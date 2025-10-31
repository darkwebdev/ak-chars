import React, { useMemo, useState } from 'react';
import Card from './components/Card';
import Filters from './components/Filters';
import charsData from '../../data/chars.json';
import tiersData from '../../data/charTiers.json';
import { Char } from '../types';

export default function App() {
  const [chars] = useState<Char[]>(() => charsData as unknown as Char[]);
  const [tiers] = useState<Record<string, string>>(
    () => tiersData as unknown as Record<string, string>,
  );
  const [rarity, setRarity] = useState('');
  const [tierFilter, setTierFilter] = useState('');

  const rarities = useMemo(
    () =>
      (Array.from(new Set(chars.map((c) => c.rarity).filter(Boolean))) as string[]).sort(
        (a, b) => Number(b.replace(/\D/g, '')) - Number(a.replace(/\D/g, '')),
      ),
    [chars],
  );
  const professions = useMemo(
    () => (Array.from(new Set(chars.map((c) => c.profession).filter(Boolean))) as string[]).sort(),
    [chars],
  );

  const [profession, setProfession] = useState(() => {
    const profs = (Array.from(new Set(chars.map((c) => c.profession).filter(Boolean))) as string[]).sort();
    return profs[0] || '';
  });
  // Extract and sort tier names dynamically, supporting modifiers like + and -
  const getTierSortValue = (tier: string): number => {
    if (!tier) return -100;
    // EX is always highest
    if (tier === 'EX') return 100;
    // S+ > S > S- > A+ > A > A- ...
    const match = tier.match(/^([A-Z]+)([+-])?$/);
    if (!match) return -100;
    const base = match[1];
    const mod = match[2] || '';
    const baseOrder = ['F', 'E', 'D', 'C', 'B', 'A', 'S'];
    let value = baseOrder.indexOf(base) * 10;
    if (mod === '+') value += 2;
    if (mod === '-') value -= 2;
    return value;
  };

  const tiersList = useMemo(() => {
    const availableTiers = Array.from(new Set(Object.values(tiers))).filter(Boolean) as string[];
    // Sort descending: higher tiers first
    return availableTiers.sort((a, b) => getTierSortValue(b) - getTierSortValue(a));
  }, [tiers]);

  const isTierEqualOrHigher = (charTier: string, minTier: string): boolean => {
    if (!charTier || !minTier) return true;
    const charValue = getTierSortValue(charTier);
    const minValue = getTierSortValue(minTier);
    return charValue >= minValue;
  };

  const filtered = chars.filter((c) => {
    if (rarity && c.rarity !== rarity) return false;
    if (profession && c.profession !== profession) return false;
    const t = tiers[c.name || ''] || '';
    if (tierFilter) {
      // If filtering by minimum tier, exclude characters with no tier
      if (!t) return false;
      if (!isTierEqualOrHigher(t, tierFilter)) return false;
    }
    return true;
  });

  // Sort by tier descending, characters with no tier at the end
  const sorted = filtered.slice().sort((a, b) => {
    const tierA = tiers[a.name || ''] || '';
    const tierB = tiers[b.name || ''] || '';
    const valA = tierA ? getTierSortValue(tierA) : -999;
    const valB = tierB ? getTierSortValue(tierB) : -999;
    return valB - valA;
  });

  return (
    <div className="app-layout">
      <aside className="profession-sidebar">
        <h3>Professions</h3>
        <div className="profession-buttons">
          {professions.map((prof) => (
            <button
              key={prof}
              className={`profession-btn ${profession === prof ? 'active' : ''}`}
              onClick={() => setProfession(prof)}
            >
              {prof}
            </button>
          ))}
        </div>
      </aside>

      <div className="main-content">
        <header>
          <h1>Arknights Characters</h1>
          <Filters
            rarity={rarity}
            setRarity={setRarity}
            rarities={rarities}
            tierFilter={tierFilter}
            setTierFilter={setTierFilter}
            tiersList={tiersList}
          />
        </header>
        <main>
          <div className="grid">
            {sorted.map((c) => (
              <Card key={c.id} ch={c} tier={tiers[c.name || '']} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
