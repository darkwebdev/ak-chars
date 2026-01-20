export default {
  testEnvironment: 'jsdom',
  rootDir: '.',
  testMatch: ['**/tests/**/*.test.ts', '**/?(*.)+(spec|test).ts', '**/?(*.)+(spec|test).tsx'],
  testPathIgnorePatterns: ['/node_modules/', '/e2e/'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  preset: 'ts-jest',
  globals: {
    'ts-jest': {
      isolatedModules: true,
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        module: 'esnext',
        target: 'esnext',
      },
    },
  },
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      isolatedModules: true,
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        module: 'esnext',
        target: 'esnext',
      },
    }],
  },
  moduleNameMapper: {
    '^rxjs$': '<rootDir>/__mocks__/rxjsMock.cjs',
    '^rxjs/operators$': '<rootDir>/__mocks__/rxjsMock.cjs',
    'utils/env$': '<rootDir>/src/client/utils/__mocks__/env.ts',
    'graphqlClient$': '<rootDir>/src/client/utils/__mocks__/graphqlClient.ts',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.svg\\?react$': '<rootDir>/__mocks__/svgMock.tsx',
    '\\.(svg|png|jpg|jpeg|gif)$': '<rootDir>/__mocks__/fileMock.js',
  },
};
