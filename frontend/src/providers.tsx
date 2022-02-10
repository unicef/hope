import { ApolloProvider } from '@apollo/react-hooks';
import MomentUtils from '@date-io/moment';
import { ThemeProvider } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { client } from './apollo/client';
import { theme } from './theme';

export const Providers: React.FC = ({ children }) => (
  <ApolloProvider client={client}>
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
          <CssBaseline />
          {children}
        </MuiPickersUtilsProvider>
      </StyledThemeProvider>
    </ThemeProvider>
  </ApolloProvider>
);
