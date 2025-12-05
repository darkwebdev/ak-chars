import { FC } from 'react';
import { ProfessionButton } from '../ProfessionButton';
import { Profession } from '../../../types';
import './style.css';

type Props = {
  professions: Profession[];
  current?: Profession;
  onSelect: (p?: Profession) => void;
};

export const Sidebar: FC<Props> = ({ professions, current, onSelect = () => {} }) => (
  <aside className="profession-sidebar">
    {professions.map((prof) => (
      <ProfessionButton
        key={prof}
        profession={prof}
        active={current === prof || (prof === 'All' && current === undefined)}
        onClick={onSelect}
      />
    ))}
  </aside>
);
