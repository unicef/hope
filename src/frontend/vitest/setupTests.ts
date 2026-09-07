import { random } from 'lodash';
import { configure } from '@testing-library/react';
import React from 'react';
import { setupServer } from 'msw/node';
import setupInternalization from '../src/i18n';
import * as useBusinessAreaModule from '../src/hooks/useBusinessArea';
import * as useGlobalProgramModule from '../src/hooks/useGlobalProgram';
import * as useProgramContextModule from '../src/programContext';
import { handlers } from '../src/mocks/handlers';
import {
  beforeAll,
  afterAll,
  afterEach,
  beforeEach,
  expect,
  vi,
} from 'vitest';
import { fakeContextProgram } from 'src/testUtils/testUtils';

global.React = React;
// Set up global mocks and configurations
global.Date.now = () => new Date('1970-01-01T00:00:00.000Z').getTime();
process.env.TZ = 'UTC';
setupInternalization();

beforeEach(() => {
  vi.spyOn(global.Math, 'random').mockImplementation(random);
  vi.spyOn(useBusinessAreaModule, 'useBusinessArea').mockReturnValue(
    'afghanistan',
  );
  vi.spyOn(useGlobalProgramModule, 'useGlobalProgram').mockReturnValue(
    'UHJvZ3JhbU5vZGU6ZTRmOGMwNjctNjcwOC00NjZmLWFjYmMtZGE2OTkxZjE0MjY2',
  );
  vi.spyOn(useProgramContextModule, 'useProgramContext').mockReturnValue(
    fakeContextProgram,
  );
});

// Mock ResizeObserver for tests that rely on it
globalThis.ResizeObserver = class {
  observe() {}

  unobserve() {}

  disconnect() {}
};

// Mock crypto.randomUUID if not available in Vitest environment
globalThis.crypto.randomUUID = () => 'd7a794d1-0ead-4424-9ff2-38d14db32b99';

// Mock Service Worker registration
const server = setupServer(...handlers);

// Establish API mocking before all tests.
beforeAll(() => server.listen());
beforeAll(() => {
  configure({ testIdAttribute: 'data-cy' });
});

// Reset any request handlers that are declared as a part of our tests
// (i.e. for testing one-time error scenarios).
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished.
afterAll(() => server.close());

// styled-components generates component ids (`sc-*`) and their paired class
// hashes from a process-global counter, so they depend on module evaluation
// order and differ between local runs and CI workers. Normalize them so DOM
// snapshots stay deterministic.
const SC_COMPONENT_ID = /^sc-[a-zA-Z]+$/;
const SC_GENERATED_CLASS = /^[a-zA-Z]{4,8}$/;

const styledClasses = (element: Element): string[] =>
  (element.getAttribute('class') || '').split(/\s+/).filter(Boolean);

const hasStyledComponentId = (element: Element): boolean =>
  styledClasses(element).some((name) => SC_COMPONENT_ID.test(name));

expect.addSnapshotSerializer({
  test: (value) =>
    value instanceof Element && hasStyledComponentId(value as Element),
  serialize: (value, config, indentation, depth, refs, printer) => {
    const clone = (value as Element).cloneNode(true) as Element;
    const normalized = styledClasses(clone)
      .filter((name) => !SC_GENERATED_CLASS.test(name))
      .map((name) => (SC_COMPONENT_ID.test(name) ? 'styled-normalized' : name));
    clone.setAttribute('class', normalized.join(' '));
    return printer(clone, config, indentation, depth, refs);
  },
});
