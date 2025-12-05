export type ThemeName = 'light' | 'dark';

export const THEME_KEY = 'ak_theme';

const PREFERS_LIGHT = '(prefers-color-scheme: light)';

function isOsLight(): boolean {
  return typeof window !== 'undefined' && window.matchMedia?.(PREFERS_LIGHT).matches === true;
}

export function getPreferredTheme(): ThemeName {
  // 1) If a data-theme attribute is present, respect it (including 'auto').
  if (typeof document !== 'undefined') {
    const attr = document.documentElement.getAttribute('data-theme');
    if (attr === 'light' || attr === 'dark') return attr;
    if (attr === 'auto') return isOsLight() ? 'light' : 'dark';
  }

  // 2) If user has explicitly chosen a theme, use it.
  try {
    if (typeof window !== 'undefined') {
      const stored = window.localStorage.getItem(THEME_KEY);
      if (stored === 'light' || stored === 'dark') return stored as ThemeName;
    }
  } catch {
    /* ignore storage errors */
  }

  // 3) Fall back to OS preference.
  return isOsLight() ? 'light' : 'dark';
}

export function applyTheme(value: ThemeName | 'auto' | undefined) {
  if (typeof document !== 'undefined') {
    if (value === 'light' || value === 'dark' || value === 'auto') {
      document.documentElement.setAttribute('data-theme', value);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }

  // Persist explicit choices; if 'auto' or undefined, remove stored preference.
  try {
    if (typeof window !== 'undefined') {
      if (value === 'light' || value === 'dark') window.localStorage.setItem(THEME_KEY, value);
      else window.localStorage.removeItem(THEME_KEY);
    }
  } catch {
    /* ignore storage errors */
  }
}

export function initOsThemeListener(): () => void {
  if (typeof window === 'undefined' || !window.matchMedia) return () => {};

  const mq = window.matchMedia(PREFERS_LIGHT);
  const onChange = () => {
    try {
      const stored = window.localStorage.getItem(THEME_KEY);
      if (stored !== 'light' && stored !== 'dark') applyTheme(isOsLight() ? 'light' : 'dark');
    } catch {
      /* ignore */
    }
  };

  mq.addEventListener?.('change', onChange as EventListener);

  return () => mq.removeEventListener?.('change', onChange as EventListener);
}
