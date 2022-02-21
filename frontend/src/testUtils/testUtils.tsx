import React, { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { render, RenderOptions } from '@testing-library/react';
import cloneDeep from 'lodash/cloneDeep';
import { TestProviders } from './testProviders';

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'queries'>,
) =>
  render(<BrowserRouter>{ui}</BrowserRouter>, {
    wrapper: TestProviders,
    ...options,
  });

export * from '@testing-library/react';
export { customRender as render };

let m_w = 123456789;
let m_z = 987654321;
const mask = 0xffffffff;

// Takes any integer
export const seed = (i) => {
  m_w = (123456789 + i) & mask;
  m_z = (987654321 - i) & mask;
};

// Returns number between 0 (inclusive) and 1.0 (exclusive),
// just like Math.random().
export const random = () => {
  m_z = (36969 * (m_z & 65535) + (m_z >> 16)) & mask;
  m_w = (18000 * (m_w & 65535) + (m_w >> 16)) & mask;
  let result = ((m_z << 16) + (m_w & 65535)) >>> 0;
  result /= 4294967296;
  return result;
};

export const makeApolloLoadingMock = (mocks) => {
  let mocksWithDelay = cloneDeep(mocks);
  for (const mock of mocksWithDelay) {
    mock.request.delay = 1e21;
  }
  return mocksWithDelay;
};
