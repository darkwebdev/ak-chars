// Provide a minimal jest global for ESM test environments when using ts-jest/vm modules.
// This uses the jest-mock package which exposes `fn`, `spyOn`, etc.
try {
  // eslint-disable-next-line global-require
  const jestMock = require('jest-mock');
  if (typeof globalThis.jest === 'undefined') {
    // attach a lightweight jest mock API
    globalThis.jest = jestMock;
  }
} catch (e) {
  // If jest-mock isn't available, tests that rely on jest globals will fail later with clearer errors.
}

// Provide missing helpers used by tests that aren't part of `jest-mock`.
if (typeof globalThis.jest !== 'undefined') {
  if (typeof globalThis.jest.restoreAllMocks !== 'function') {
    globalThis.jest.restoreAllMocks = () => {};
  }
}
