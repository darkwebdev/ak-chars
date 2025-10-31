import React from 'react';

export default function Filters({
  rarity,
  setRarity,
  rarities,
  tierFilter,
  setTierFilter,
  tiersList,
}: {
  rarity: string;
  setRarity: (v: string) => void;
  rarities: string[];
  tierFilter: string;
  setTierFilter: (v: string) => void;
  tiersList: string[];
}) {
  return (
    <div className="filters">
      <label>
        Rarity{' '}
        <select value={rarity} onChange={(e) => setRarity(e.target.value)}>
          <option value="">All</option>
          {rarities.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </label>
      <label>
        Minimum Tier{' '}
        <select value={tierFilter} onChange={(e) => setTierFilter(e.target.value)}>
          <option value="">All</option>
          {tiersList.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
