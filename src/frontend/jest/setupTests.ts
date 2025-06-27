import '@testing-library/jest-dom';
import 'jest-canvas-mock';
import setupInternalization from '../src/i18n';
import { fakeContextProgram, random, seed } from '../src/testUtils/testUtils';
import * as useBusinessAreaModule from '../src/hooks/useBusinessArea';
import * as useGlobalProgramModule from '../src/hooks/useGlobalProgram';
import { fakeProgram } from '../fixtures/programs/fakeProgram';
import * as useProgramContextModule from '../src/programContext';
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
} from 'chart.js';
import * as usePermissionsModule from '@hooks/usePermissions';

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

globalThis.ResizeObserver = class {
  observe() {}

  unobserve() {}

  disconnect() {}
};

globalThis.crypto.randomUUID = () => 'd7a794d1-0ead-4424-9ff2-38d14db32b99';

ChartJS.register(ArcElement, LinearScale, CategoryScale, BarElement);
