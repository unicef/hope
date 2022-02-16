import React, { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { render, RenderOptions } from '@testing-library/react';
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
