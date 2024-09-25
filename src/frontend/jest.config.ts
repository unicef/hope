/* eslint-disable */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jest-environment-jsdom',
  collectCoverage: true,
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}'],
  moduleDirectories: ['node_modules', 'src'],
  testPathIgnorePatterns: ['/node_modules/', '/.history/'],
  setupFilesAfterEnv: ['./jest/setupTests.ts'],
  transform: {
    '^.+\\.cjs$': 'babel-jest',
    '^.+\\.(js|jsx)$': 'esbuild-jest',
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.css$': '<rootDir>/config/jest/cssTransform.cjs',
    '^(?!.*\\.(js|jsx|ts|tsx|css|json)$)':
      '<rootDir>/config/jest/fileTransform.cjs',
  },
  transformIgnorePatterns: [
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|ts|tsx)$',
    '^.+\\.module\\.(css|sass|scss)$',
  ],
  coveragePathIgnorePatterns: [
    '/node_modules/.*',
    '/script/',
    '/src/serviceWorker.ts',
    '.*\\.d\\.ts',
  ],
  moduleNameMapper: {
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@core/(.*)$': '<rootDir>/src/components/core/$1',
    '^@containers/(.*)$': '<rootDir>/src/containers/$1',
    '^@shared/(.*)$': '<rootDir>/src/shared/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@generated/(.*)$': '<rootDir>/src/__generated__/$1',
  },
};
