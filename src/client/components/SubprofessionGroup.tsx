import React from 'react';
import Card from './Card';
import type { Char } from '../../types';

type Props = {
  name: string;
  chars: Char[];
  tiers: Record<string, string>;
  owned: string[];
  onToggleOwned: (id: string) => void;
};

export default function SubprofessionGroup({ name, chars, tiers, owned, onToggleOwned }: Props) {
  const total = chars.length;
  const ownedCount = chars.filter((c) => owned.includes(c.id)).length;

  return (
    <section className="subgroup">
      <h4 className="subprofession-header">
        {name === 'Other' ? 'General' : name}
        <span className="ownedCount">
          Owned: {ownedCount}/{total}
        </span>
      </h4>
      <div className="grid">
        {chars.map((c) => (
          <Card
            key={c.id}
            ch={c}
            tier={tiers[c.name || '']}
            owned={owned.includes(c.id)}
            onToggleOwned={onToggleOwned}
          />
        ))}
      </div>
    </section>
  );
}
