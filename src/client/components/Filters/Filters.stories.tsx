import React from 'react';
import { Filters } from './index';

export default {
  title: 'Components/Filters',
  component: Filters,
};

export const Default = () => (
  <Filters
    rarity={''}
    setRarity={() => {}}
    rarities={['1', '3', '5']}
    tierFilter={''}
    setTierFilter={() => {}}
    tiersList={['S', 'A', 'B']}
    groupBySubprof={true}
    setGroupBySubprof={() => {}}
  />
);
