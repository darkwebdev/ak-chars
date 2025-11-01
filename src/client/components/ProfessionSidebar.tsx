import React from 'react';

type Props = {
  professions: string[];
  current: string;
  onSelect: (p: string) => void;
};

export default function ProfessionSidebar({ professions, current, onSelect }: Props) {
  return (
    <aside className="profession-sidebar">
      <h3>Professions</h3>
      <div className="profession-buttons">
        {professions.map((prof) => (
          <button
            key={prof}
            className={`profession-btn ${current === prof ? 'active' : ''}`}
            onClick={() => onSelect(prof)}
          >
            {prof}
          </button>
        ))}
      </div>
    </aside>
  );
}
