// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import React, { ReactElement } from 'react';
import { Router } from 'react-router-dom';
import '@testing-library/jest-dom/extend-expect';
import { configure, render } from '@testing-library/react';
import '@testing-library/jest-dom';
configure({ testIdAttribute: 'data-cy' });

export const renderWithRouter = (ui: ReactElement) => ({
  ...render(<Router>{ui}</Router>),
});
