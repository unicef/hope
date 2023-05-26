import { ApolloProvider } from '@apollo/react-hooks';
import MomentUtils from '@date-io/moment';
import { ThemeProvider } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import moment from 'moment';
import React, { useEffect, useState } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import ApolloClient from 'apollo-client';
import { NormalizedCacheObject } from 'apollo-cache-inmemory';
import { getClient } from './apollo/client';
import { ConfirmationDialogProvider } from './components/core/ConfirmationDialog';
import { theme } from './theme';
import {ReactFCWithChildren} from "./utils/types";

export const Providers: ReactFCWithChildren = ({ children }) => {
  const [apolloClient, setApolloClient] = useState<
    ApolloClient<NormalizedCacheObject>
  >();
  useEffect(() => {
    getClient().then((client) => {
      setApolloClient(client);
    });
  }, []);
  if (!apolloClient) {
    return null;
  }
  return (
    <ApolloProvider client={apolloClient}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
            <ConfirmationDialogProvider>
              <CssBaseline />
              {children}
            </ConfirmationDialogProvider>
          </MuiPickersUtilsProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
