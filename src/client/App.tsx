import { useState } from 'react';
import { Filters } from './components/Filters';
import AuthPage from './components/AuthPage';
import { SubprofessionGroup } from './components/SubprofessionGroup';
import { groupsWithMeta, buildGroupsByKey } from './utils/groupHelpers';
import {
  getRarities,
  getProfessions,
  getTiersList,
  filterChars,
  sortByTier,
} from './utils/appHelpers';
import { Sidebar } from './components/Sidebar';
import { ThemeToggle } from './components/ThemeToggle';
import { GraphQLRosterButton } from './components/GraphQLRosterButton';
import { useLocalStorage } from './hooks/useLocalStorage';
import charsData from '../../data/chars.json';
import tiersData from '../../data/charTiers.json';
import professionsData from '../../data/professions.json';
import { Char } from '../types';

export function App() {
  const [chars] = useState<Char[]>(charsData);
  const [tiers] = useState<Record<string, string>>(tiersData);
  const [rarity, setRarity] = useState('');
  const [tierFilter, setTierFilter] = useState('');

  const rarities = getRarities(chars);
  const professions = getProfessions(chars);
  const professionsWithAll = ['All', ...professions];
  const [profession, setProfession] = useState(professionsWithAll[0] || '');

  const [search, setSearch] = useState('');
  const [groupBySubprof, setGroupBySubprof] = useLocalStorage<boolean>('groupBySubprof', true);

  const [ownedIds, setOwnedIds] = useLocalStorage<string[]>('ownedChars', []);

  const toggleOwned = (id: string) => {
    setOwnedIds((prev) => {
      const arr = prev || [];
      if (arr.includes(id)) return arr.filter((x) => x !== id);
      return [...arr, id];
    });
  };

  const tiersList = getTiersList(tiers);

  const filtered = filterChars(chars, rarity, profession, tierFilter, tiers, search);
  const sorted = sortByTier(filtered, tiers);
  let groups = groupsWithMeta(sorted, tiers, ownedIds);

  const subprofLookup = new Map<string, string>();
  const professionsArray = professionsData as unknown as Array<{
    subProfessionId?: string;
    subProfessionName?: string;
  }>;
  for (const p of professionsArray) {
    if (p && p.subProfessionId)
      subprofLookup.set(p.subProfessionId, p.subProfessionName || p.subProfessionId);
  }

  if (profession === 'All') {
    if (!groupBySubprof) {
      // When 'All' is selected but grouping-by-subprofession is disabled,
      // show a single flat group containing all visible characters.
      groups = [
        {
          key: 'All',
          chars: sorted,
          total: sorted.length,
          ownedCount: sorted.filter((c) => ownedIds.includes(c.id)).length,
          maxTierValue: 0,
        },
      ];
    } else {
      // Group by profession when showing all
      const profGroups = buildGroupsByKey(sorted, (ch) => ch.profession || 'Other');
      groups = Object.keys(profGroups).map((k) => {
        const arr = profGroups[k];
        const total = arr.length;
        const ownedCount = arr.filter((c) => ownedIds.includes(c.id)).length;
        const maxTierValue = 0;
        // When showing all professions, we use profession names as keys (they are already readable)
        return { key: k, chars: arr, total, ownedCount, maxTierValue };
      });
      groups.sort((a, b) => a.key.localeCompare(b.key));
    }
  } else if (!groupBySubprof) {
    // If grouping by subprofession is disabled, show a single group for the selected profession
    groups = [
      {
        key: profession,
        chars: sorted,
        total: sorted.length,
        ownedCount: sorted.filter((c) => ownedIds.includes(c.id)).length,
        maxTierValue: 0,
      },
    ];
  }

  return window.location.pathname.endsWith('/auth') ? (
    <AuthPage />
  ) : (
    <div className="app-layout">
      <div className="global-theme-toggle">
        <ThemeToggle />
      </div>
      <Sidebar professions={professionsWithAll} current={profession} onSelect={setProfession} />

      <div className="main-content">
        <header>
          <h1>Arknights Characters</h1>
          <div style={{ marginTop: 8 }}>
            <input
              type="search"
              placeholder="Start typing character name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ padding: '6px 8px', width: 260 }}
            />
          </div>
          <GraphQLRosterButton
            chars={chars.map((c) => ({ id: c.id, name: c.name || '' }))}
            onApply={(importedIds: string[]) => {
              setOwnedIds(importedIds);
            }}
          />
          <Filters
            rarity={rarity}
            setRarity={setRarity}
            rarities={rarities}
            tierFilter={tierFilter}
            setTierFilter={setTierFilter}
            tiersList={tiersList}
            groupBySubprof={groupBySubprof}
            setGroupBySubprof={setGroupBySubprof}
          />
        </header>
        <main>
          <div className="groups">
            {groups.map((g) => {
              // g.key is usually a subProfessionId when grouped by subprofession;
              // map it to a readable name if available
              const displayName = subprofLookup.get(g.key) || g.key;
              return (
                <SubprofessionGroup
                  key={g.key}
                  name={displayName}
                  chars={g.chars}
                  tiers={tiers}
                  owned={ownedIds}
                  onToggleOwned={toggleOwned}
                />
              );
            })}
          </div>
        </main>
      </div>
    </div>
  );
}
