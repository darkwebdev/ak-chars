import React from 'react';
import Stars from './Stars';
import { Char } from '../../types';

export default function Card({ ch, tier }: { ch: Char; tier?: string }) {
  return (
    <div className="card">
      <div className="avatarWrap">
        <img src={`/avatars/${ch.id}.jpg`} alt={ch.name ?? ''} />
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
