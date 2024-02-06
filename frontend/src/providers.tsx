import { ApolloProvider, ApolloClient, NormalizedCacheObject } from '@apollo/client';
import { ThemeProvider, CssBaseline } from '@mui/material';
import React, { ReactNode, useEffect, useState } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { getClient } from './apollo/client';
import { ConfirmationDialogProvider } from './components/core/ConfirmationDialog';
import { theme } from './theme';
import { ProgramProvider } from './programContext';

interface ProvidersProps {
  children: ReactNode;
}

export const Providers: React.FC<ProvidersProps> = ({ children }) => {
  const [apolloClient, setApolloClient] = useState<
  ApolloClient<NormalizedCacheObject> | undefined
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
          <ConfirmationDialogProvider>
            <CssBaseline />
            <ProgramProvider>{children}</ProgramProvider>
          </ConfirmationDialogProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
