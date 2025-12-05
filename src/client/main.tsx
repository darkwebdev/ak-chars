import React from 'react';
import { createRoot } from 'react-dom/client';
import { getPreferredTheme, applyTheme, initOsThemeListener } from './theme/theme';
import { App } from './App';
import { ThemeProvider } from './theme/ThemeProvider';
import './styles.css';

const initialTheme = getPreferredTheme();
applyTheme(initialTheme);

const cleanup = initOsThemeListener();

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);

// HMR cleanup
if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    cleanup();
  });
}
