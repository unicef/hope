import { ApolloProvider } from '@apollo/react-hooks';
import MomentUtils from '@date-io/moment';
import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { MuiPickersUtilsProvider } from '@mui/pickers';
import moment from 'moment';
import React, { useEffect, useState } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import ApolloClient from 'apollo-client';
import { NormalizedCacheObject } from 'apollo-cache-inmemory';
import { getClient } from './apollo/client';
import { ConfirmationDialogProvider } from './components/core/ConfirmationDialog';
import { theme } from './theme';

export const Providers: React.FC = ({
  children,
}: {
  children: React.ReactElement;
}) => {
  const [apolloClient, setApolloClient] =
    useState<ApolloClient<NormalizedCacheObject>>();
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
