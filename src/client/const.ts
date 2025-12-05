import { Profession } from '../types';

export const Professions = [
  'pioneer',
  'warrior',
  'tank',
  'sniper',
  'caster',
  'medic',
  'support',
  'special',
] as const;

export const ProfessionNames: Record<Profession, string> = {
  pioneer: 'Vanguard',
  warrior: 'Guard',
  tank: 'Defender',
  sniper: 'Sniper',
  caster: 'Caster',
  medic: 'Medic',
  support: 'Support',
  special: 'Specialist',
};
