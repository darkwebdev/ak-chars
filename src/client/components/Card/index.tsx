import React from 'react';
import { Stars } from '../Stars';
import { Char } from '../../../types.js';
import { getBaseUrl } from '../../utils/env';
import './style.css';

// eslint-disable-next-line no-unused-vars
type ToggleFn = (id: string) => void;

export function Card({
  ch,
  tier,
  owned,
  onToggleOwned,
}: {
  ch: Char;
  tier?: string;
  owned?: boolean;
  onToggleOwned?: ToggleFn;
}) {
  const handleClick = () => {
    if (!onToggleOwned) return;
    onToggleOwned(ch.id);
  };

  const getTierClass = (tierValue?: string) => {
    if (!tierValue) return '';
    const normalized = tierValue.toUpperCase();
    if (normalized.startsWith('EX')) return 'tier-ex';
    if (normalized.startsWith('S')) return 'tier-s';
    if (normalized.startsWith('A')) return 'tier-a';
    if (normalized.startsWith('B')) return 'tier-b';
    if (normalized.startsWith('C')) return 'tier-c';
    return 'tier-def';
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
      <div className="cardHeader">
        <Stars rarity={(ch.rarity ?? undefined) as string | undefined} />
      </div>
      <div className="avatarWrap">
        <img src={`${getBaseUrl()}avatars/${ch.id}.png`} alt={ch.name ?? ''} />
      </div>
      <div className="cardFooter">
        <div className="title">{ch.name}</div>
        <div className="meta">
          {/* <div className="profession">{ch.profession}</div> */}
          {/* <div className="subprofession">{ch.subProfessionId}</div> */}
        </div>
      </div>
      {tier && <div className={`tierBadge ${getTierClass(tier)}`}>{tier}</div>}
    </div>
  );
}
