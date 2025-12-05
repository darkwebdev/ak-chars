import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import IconMoon from './icon-moon.svg?react';
import IconSun from './icon-sun.svg?react';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className }) => {
  const { theme, toggle } = useTheme();

  const isLight = theme === 'light';

  return (
    <button
      aria-label="Toggle theme"
      title="Toggle theme"
      onClick={() => toggle()}
      className={className ? `theme-toggle ${className}` : 'theme-toggle'}
      style={{
        background: 'transparent',
        border: 'none',
        padding: 6,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        color: 'var(--text, #e6eef6)',
      }}
    >
      {isLight ? (
        <IconMoon className="theme-toggle__icon" width={20} height={20} />
      ) : (
        <IconSun className="theme-toggle__icon" width={20} height={20} />
      )}
    </button>
  );
};
