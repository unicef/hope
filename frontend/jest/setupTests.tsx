// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import React, { ReactElement } from 'react';
import { Router } from 'react-router-dom';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import '@testing-library/jest-dom/extend-expect';
import { configure, render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ApolloProvider } from '@apollo/react-hooks';
import MomentUtils from '@date-io/moment';
import { CssBaseline } from '@material-ui/core';
import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import { ThemeProvider } from '@material-ui/styles';
import moment from 'moment';
import { client } from '../src/apollo/client';
import { AutoLogout } from '../src/components/core/AutoLogout';
import { theme } from '../src/theme';

configure({ testIdAttribute: 'data-cy' });

export const renderWithRouter = (ui: ReactElement) => ({
  ...render(
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
            <CssBaseline />
            <AutoLogout />
            <Router>{ui}</Router>
          </MuiPickersUtilsProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>,
  ),
});
