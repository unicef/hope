// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import replaceAllInserter from 'string.prototype.replaceall';
import '@testing-library/jest-dom/extend-expect';
import 'jest-canvas-mock';
import setupInternalization from '../src/i18n';
import { random, seed } from '../src/testUtils/testUtils';
import * as useBusinessAreaModule from '../src/hooks/useBusinessArea';
import * as useGlobalProgramModule from '../src/hooks/useGlobalProgram';
import { fakeProgram } from '../fixtures/programs/fakeProgram';

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
});
