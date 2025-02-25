import * as usePermissionsModule from '@hooks/usePermissions';
import '@testing-library/jest-dom';
import { fakeProgram } from '../fixtures/programs/fakeProgram';
import 'jest-canvas-mock';
import { random } from 'lodash';
import setupInternalization from 'src/i18n';
import { fakeContextProgram, seed } from 'src/testUtils/testUtils';
import * as useBusinessAreaModule from '../src/hooks/useBusinessArea';
import * as useGlobalProgramModule from '../src/hooks/useGlobalProgram';
import * as useProgramContextModule from '../src/programContext';

// ✅ Mock gql function from @apollo/client
jest.mock('@apollo/client', () => {
  const actualApollo = jest.requireActual('@apollo/client');
  return {
    ...actualApollo,
    gql: (literals) => literals[0],
    ApolloLink: {
      ...actualApollo.ApolloLink,
      from: jest.fn(() => ({
        request: (operation, forward) => forward(operation),
      })),
    },
  };
});

// ✅ Mock MockLink from @apollo/client/testing
jest.mock('@apollo/client/testing', () => {
  const actualApolloTesting = jest.requireActual('@apollo/client/testing');
  return {
    ...actualApolloTesting,
    MockLink: actualApolloTesting.MockLink, // Ensure MockLink is passed through
  };
});

// ✅ Mock onError from @apollo/client/link/error
jest.mock('@apollo/client/link/error', () => {
  return {
    onError: jest.fn(() => () => {}), // Mock onError as a no-op function
  };
});

// ✅ Set up global mocks and configurations
global.Date.now = () => new Date('1970-01-01T00:00:00.000Z').getTime();
process.env.TZ = 'UTC';
setupInternalization();

global.beforeEach(() => {
  seed(0);
  jest.spyOn(global.Math, 'random').mockImplementation(random);
  jest
    .spyOn(useBusinessAreaModule, 'useBusinessArea')
    .mockReturnValue('afghanistan');
  jest
    .spyOn(useGlobalProgramModule, 'useGlobalProgram')
    .mockReturnValue(fakeProgram.id);
  jest
    .spyOn(useProgramContextModule, 'useProgramContext')
    .mockReturnValue(fakeContextProgram);
  jest.spyOn(usePermissionsModule, 'usePermissions').mockReturnValue([]);
});

// ✅ Mock ResizeObserver for tests that rely on it
globalThis.ResizeObserver = class {
  observe() {}

  unobserve() {}

  disconnect() {}
};

// ✅ Mock crypto.randomUUID if not available in Jest environment
globalThis.crypto.randomUUID = () => 'd7a794d1-0ead-4424-9ff2-38d14db32b99';
