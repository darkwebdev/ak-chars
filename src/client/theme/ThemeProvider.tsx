import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { ThemeName, getPreferredTheme, applyTheme, initOsThemeListener } from './theme';

type ThemeContextShape = {
  theme: ThemeName;
  setTheme: React.Dispatch<React.SetStateAction<ThemeName>>;
  toggle: () => ThemeName;
};

const ThemeContext = createContext<ThemeContextShape | undefined>(undefined);

export const ThemeProvider: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<ThemeName>(() => getPreferredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    return initOsThemeListener();
  }, []);

  useEffect(() => {
    // Sanitize any existing 'undefined' value and watch for future writes
    // that may set data-theme to the literal string 'undefined'. If seen,
    // remove it so CSS media queries and the addon-driven 'auto' can take effect.
    if (typeof document === 'undefined' || typeof MutationObserver === 'undefined') return;
    const el = document.documentElement;
    try {
      const attr = el.getAttribute('data-theme');
      if (attr === 'undefined') el.removeAttribute('data-theme');
    } catch {
      // ignore
    }

    const obs = new MutationObserver((records) => {
      for (const r of records) {
        if (r.type === 'attributes' && r.attributeName === 'data-theme') {
          try {
            const v = el.getAttribute('data-theme');
            if (v === 'undefined') {
              el.removeAttribute('data-theme');
              // eslint-disable-next-line no-console
              console.warn('Removed invalid data-theme="undefined" attribute');
            }
          } catch {
            // ignore
          }
        }
      }
    });
    obs.observe(el, { attributes: true });
    return () => obs.disconnect();
  }, []);

  const toggle = () => {
    const next: ThemeName = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    return next;
  };

  const value = useMemo(() => ({ theme, setTheme, toggle }), [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    // eslint-disable-next-line no-console
    console.warn('useTheme called outside ThemeProvider — returning fallback theme.');
    return {
      theme: getPreferredTheme(),
      setTheme: (() => {}) as React.Dispatch<React.SetStateAction<ThemeName>>,
      toggle: () => getPreferredTheme(),
    } as ThemeContextShape;
  }
  return ctx;
}
