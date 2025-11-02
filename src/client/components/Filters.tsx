import React from 'react';

// eslint-disable-next-line no-unused-vars
type SetString = (v: string) => void;

export function Filters({
  rarity,
  setRarity,
  rarities,
  tierFilter,
  setTierFilter,
  tiersList,
}: {
  rarity: string;
  setRarity: SetString;
  rarities: string[];
  tierFilter: string;
  setTierFilter: SetString;
  // Note: parameter names in function types intentionally use underscore to avoid unused-var warnings
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
