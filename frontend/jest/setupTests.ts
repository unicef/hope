import '@testing-library/jest-dom';
import 'jest-canvas-mock';
import replaceAllInserter from 'string.prototype.replaceall';
import setupInternalization from '../src/i18n';
import { fakeContextProgram, random, seed } from '../src/testUtils/testUtils';
import * as useBusinessAreaModule from '../src/hooks/useBusinessArea';
import * as useGlobalProgramModule from '../src/hooks/useGlobalProgram';
import { fakeProgram } from '../fixtures/programs/fakeProgram';
import * as useProgramContextModule from '../src/programContext';

global.Date.now = () => new Date('1970-01-01T00:00:00.000Z').getTime();
replaceAllInserter.shim();
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
});
