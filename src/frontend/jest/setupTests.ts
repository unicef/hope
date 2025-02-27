// import * as usePermissionsModule from '@hooks/usePermissions';
import '@testing-library/jest-dom';
import 'jest-canvas-mock';
import { random } from 'lodash';
import setupInternalization from '../src/i18n';
// import { seed } from '../src/testUtils/testUtils';
import * as useBusinessAreaModule from '../src/hooks/useBusinessArea';
import * as useGlobalProgramModule from '../src/hooks/useGlobalProgram';
// import * as useProgramContextModule from '../src/programContext';

// // ✅ Set up global mocks and configurations
global.Date.now = () => new Date('1970-01-01T00:00:00.000Z').getTime();
process.env.TZ = 'UTC';
setupInternalization();

global.beforeEach(() => {
  // seed(0);
  jest.spyOn(global.Math, 'random').mockImplementation(random);
  jest
    .spyOn(useBusinessAreaModule, 'useBusinessArea')
    .mockReturnValue('afghanistan');
  jest
    .spyOn(useGlobalProgramModule, 'useGlobalProgram')
    .mockReturnValue(
      'UHJvZ3JhbU5vZGU6ZTRmOGMwNjctNjcwOC00NjZmLWFjYmMtZGE2OTkxZjE0MjY2',
    );
  // jest
  //   .spyOn(useProgramContextModule, 'useProgramContext')
  //   .mockReturnValue({} as any);
  // jest.spyOn(usePermissionsModule, 'usePermissions').mockReturnValue([]);
});

// ✅ Mock ResizeObserver for tests that rely on it
globalThis.ResizeObserver = class {
  observe() {}

  unobserve() {}

  disconnect() {}
};

// ✅ Mock crypto.randomUUID if not available in Jest environment
globalThis.crypto.randomUUID = () => 'd7a794d1-0ead-4424-9ff2-38d14db32b99';
