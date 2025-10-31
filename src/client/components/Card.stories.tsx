import React from 'react';
import Card from './Card';
import type { Char } from '../../types';

export default {
  title: 'Components/Card',
  component: Card,
};

const mock: Char = {
  id: 'char_285_medic2',
  name: 'Lancet-2',
  rarity: 'TIER_1',
  profession: 'MEDIC',
  subProfessionId: 'physician',
};

export const Default = () => <Card ch={mock} tier={'A'} />;
