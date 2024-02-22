import {
  ApolloProvider,
  ApolloClient,
  NormalizedCacheObject,
} from '@apollo/client';
import { CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { ReactNode, useEffect, useState } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { getClient } from './apollo/client';
import { ConfirmationDialogProvider } from '@core/ConfirmationDialog';
import { theme } from './theme';
import { ProgramProvider } from './programContext';
import { SnackbarProvider } from '@hooks/useSnackBar';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';

interface ProvidersProps {
  children: ReactNode[];
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
            <LocalizationProvider dateAdapter={AdapterMoment}>
              <CssBaseline />
              <ProgramProvider>
                <SnackbarProvider>{children}</SnackbarProvider>
              </ProgramProvider>
            </LocalizationProvider>
          </ConfirmationDialogProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
