import React from 'react';
import { Card } from './index';
import type { Char } from '../../../types.js';

export default {
  title: 'Components/Card',
  component: Card,
};

const lancet: Char = {
  id: 'char_285_medic2',
  name: 'Lancet-2',
  rarity: 'TIER_1',
  profession: 'MEDIC',
  subProfessionId: 'physician',
};

const exusiai: Char = {
  id: 'char_103_angel',
  name: 'Exusiai',
  rarity: 'TIER_6',
  profession: 'SNIPER',
  subProfessionId: 'fastshot',
};

const texas: Char = {
  id: 'char_102_texas',
  name: 'Texas',
  rarity: 'TIER_5',
  profession: 'PIONEER',
  subProfessionId: 'pioneer',
};

const meteor: Char = {
  id: 'char_126_shotst',
  name: 'Meteor',
  rarity: 'TIER_4',
  profession: 'SNIPER',
  subProfessionId: 'fastshot',
};

const orchid: Char = {
  id: 'char_278_orchid',
  name: 'Orchid',
  rarity: 'TIER_3',
  profession: 'SUPPORT',
  subProfessionId: 'slower',
};

const wisadel: Char = {
  id: 'char_1035_wisdel',
  name: "Wiš'adel",
  rarity: 'TIER_6',
  profession: 'SNIPER',
  subProfessionId: 'bombarder',
};

export const MultipleCards = () => (
  <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
    <Card ch={lancet} />
    <Card ch={orchid} tier={'B'} owned={true} />
    <Card ch={meteor} tier={'A'} />
    <Card ch={texas} tier={'S'} owned={true} />
    <Card ch={exusiai} tier={'S+'} />
    <Card ch={wisadel} tier={'EX'} owned={true} />
  </div>
);

export const WithToggle = () => {
  const [owned, setOwned] = React.useState(false);
  return <Card ch={exusiai} tier={'S+'} owned={owned} onToggleOwned={() => setOwned(!owned)} />;
};
