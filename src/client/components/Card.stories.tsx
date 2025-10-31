import React from 'react';
import Card from './Card';

export default {
  title: 'Components/Card',
  component: Card,
};

const mock = {
  id: 'char_285_medic2',
  name: 'Lancet-2',
  rarity: 'TIER_1',
  profession: 'MEDIC',
  subProfessionId: 'physician',
};

export const Default = () => <Card ch={mock as any} tier={'A'} />;
