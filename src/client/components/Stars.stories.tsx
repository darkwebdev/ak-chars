import React from 'react';
import { Stars } from './Stars';

export default {
  title: 'Components/Stars',
  component: Stars,
};

export const OneStar = () => <Stars rarity="1" />;
export const ThreeStar = () => <Stars rarity="3" />;
export const SixStar = () => <Stars rarity="6" />;
