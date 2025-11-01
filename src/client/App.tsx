import React, { useState } from 'react';
import Filters from './components/Filters';
import SubprofessionGroup from './components/SubprofessionGroup';
import { groupsWithMeta } from './utils/groupHelpers';
import {
  getRarities,
  getProfessions,
  getTiersList,
  filterChars,
  sortByTier,
} from './utils/appHelpers';
import ProfessionSidebar from './components/ProfessionSidebar';
import useLocalStorage from './hooks/useLocalStorage';
import charsData from '../../data/chars.json';
import tiersData from '../../data/charTiers.json';
import { Char } from '../types';

export default function App() {
  const [chars] = useState<Char[]>(charsData);
  const [tiers] = useState<Record<string, string>>(tiersData);
  const [rarity, setRarity] = useState('');
  const [tierFilter, setTierFilter] = useState('');

  const rarities = getRarities(chars);
  const professions = getProfessions(chars);
  const [profession, setProfession] = useState(professions[0] || '');

  const [ownedIds, setOwnedIds] = useLocalStorage<string[]>('ownedChars', []);

  const toggleOwned = (id: string) => {
    setOwnedIds((prev) => {
      const arr = prev || [];
      if (arr.includes(id)) return arr.filter((x) => x !== id);
      return [...arr, id];
    });
  };

  const tiersList = getTiersList(tiers);

  const filtered = filterChars(chars, rarity, profession, tierFilter, tiers);
  const sorted = sortByTier(filtered, tiers);
  const groups = groupsWithMeta(sorted, tiers, ownedIds);

  return (
    <div className="app-layout">
      <ProfessionSidebar professions={professions} current={profession} onSelect={setProfession} />

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
          <div className="groups">
            {groups.map((g) => (
              <SubprofessionGroup
                key={g.key}
                name={g.key}
                chars={g.chars}
                tiers={tiers}
                owned={ownedIds}
                onToggleOwned={toggleOwned}
              />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
