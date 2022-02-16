// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import replaceAllInserter from 'string.prototype.replaceall';
import '@testing-library/jest-dom/extend-expect';
import 'jest-canvas-mock';
import setupInternalization from '../src/i18n';

global.Date.now = () => new Date('1970-01-01T00:00:00.000Z').getTime();
replaceAllInserter.shim();
setupInternalization();
