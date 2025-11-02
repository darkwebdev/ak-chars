export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'jsdom',
  rootDir: '.',
  testMatch: ['**/tests/**/*.test.ts', '**/?(*.)+(spec|test).ts'],
  extensionsToTreatAsEsm: ['.ts'],
  injectGlobals: true,
  transform: {
    '^.+\\.ts$': ['ts-jest', { useESM: true }],
  },
};
