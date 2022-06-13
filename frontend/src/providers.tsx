import { ApolloProvider } from '@apollo/react-hooks';
import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
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
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <ConfirmationDialogProvider>
              <CssBaseline />
              {children}
            </ConfirmationDialogProvider>
          </LocalizationProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
