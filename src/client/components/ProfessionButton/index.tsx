import React, { FC } from 'react';
import IconVanguard from './icons/icon-vanguard.svg?react';
import IconGuard from './icons/icon-guard.svg?react';
import IconSniper from './icons/icon-sniper.svg?react';
import IconCaster from './icons/icon-caster.svg?react';
import IconMedic from './icons/icon-medic.svg?react';
import IconSupport from './icons/icon-support.svg?react';
import IconSpecialist from './icons/icon-specialist.svg?react';
import IconDefender from './icons/icon-defender.svg?react';
import { Profession } from '../../../types';
import { ProfessionNames } from '../../const';
import './style.css';

type Props = {
  profession?: Profession;
  active?: boolean;
  onClick?: (profession?: Profession) => void;
};

type IconMapType = React.FC<React.SVGProps<SVGSVGElement>>;

const IconMap: Record<Profession, IconMapType> = {
  pioneer: IconVanguard as unknown as IconMapType,
  warrior: IconGuard as unknown as IconMapType,
  sniper: IconSniper as unknown as IconMapType,
  caster: IconCaster as unknown as IconMapType,
  medic: IconMedic as unknown as IconMapType,
  support: IconSupport as unknown as IconMapType,
  special: IconSpecialist as unknown as IconMapType,
  tank: IconDefender as unknown as IconMapType,
};
export const ProfessionButton: FC<Props> = ({ profession, active, onClick = () => {} }) => {
  const IconComp = IconMap[profession];

  return (
    <button
      className={`profession-btn ${active ? 'active' : ''}`}
      onClick={() => onClick(profession)}
      title={profession ? ProfessionNames[profession] : undefined}
    >
      {IconComp ? (
        <IconComp
          className="profession-icon"
          aria-hidden={false}
          role="img"
          aria-label={ProfessionNames[profession]}
        />
      ) : (
        <span className="profession-text">All</span>
      )}
    </button>
  );
};
