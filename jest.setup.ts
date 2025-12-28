import '@testing-library/jest-dom';

// Set NODE_ENV for test environment checks
process.env.NODE_ENV = 'test';

// Mock import.meta.env for Vite
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        BASE_URL: '/',
        DEV: true,
        PROD: false,
        MODE: 'test',
        SSR: false,
      },
    },
  },
  writable: false,
  configurable: true,
});
