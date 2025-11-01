import React from 'react';
import Stars from './Stars';
import { Char } from '../../types';

export default function Card({
  ch,
  tier,
  owned,
  onToggleOwned,
}: {
  ch: Char;
  tier?: string;
  owned?: boolean;
  onToggleOwned?: (id: string) => void;
}) {
  const handleClick = () => {
    if (!onToggleOwned) return;
    onToggleOwned(ch.id);
  };

  return (
    <div
      className={`card ${owned ? 'owned' : ''}`}
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
      aria-pressed={owned ? 'true' : 'false'}
      aria-label={`${ch.name} ${owned ? 'owned' : 'not owned'}`}
    >
      <div className="avatarWrap">
        <img src={`${import.meta.env.BASE_URL}avatars/${ch.id}.jpg`} alt={ch.name ?? ''} />
        {owned && <div className="ownedBadge">✓</div>}
      </div>
      <div className="info">
        <div className="title">{ch.name}</div>
        <div className="meta">
          <div className="rarity">
            <Stars rarity={(ch.rarity ?? undefined) as string | undefined} />
          </div>
          <div className="profession">{ch.profession}</div>
          <div className="subprofession">{ch.subProfessionId}</div>
        </div>
        <div className="tier">Tier: {tier || '—'}</div>
      </div>
    </div>
  );
}
