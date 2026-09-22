import {
  MutationCache,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { isStaticReferenceQuery } from '@utils/queryCacheUtils';
import { showApiErrorMessages } from '@utils/utils';
import { CssBaseline } from '@mui/material';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import type { FC, ReactNode } from 'react';
import { useState } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { ConfirmationDialogProvider } from '@core/ConfirmationDialog';
import { theme } from './theme';
import { ProgramProvider } from './programContext';
import { SnackbarProvider, useSnackbar } from '@hooks/useSnackBar';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface ProvidersProps {
  children: ReactNode[];
}

// Safety net for eventual freshness only: `refetchType: 'none'` marks queries stale without
// refetching, so it never re-fires a GET on a just-deleted resource. Targeted per-flow
// invalidations still do the immediate on-screen refresh.
function createQueryClient(showMessage: (msg: string) => void): QueryClient {
  const queryClient: QueryClient = new QueryClient({
    mutationCache: new MutationCache({
      onSuccess: () => {
        queryClient.invalidateQueries({
          predicate: (query) => !isStaticReferenceQuery(query.queryKey),
          refetchType: 'none',
        });
      },
      // Default error path: without it a backend 4xx on a mutation that defines no
      // `onError` is invisible to the user and only shows up in Sentry.
      onError: (error, _variables, _onMutateResult, mutation) => {
        if (mutation.options.onError) return;
        showApiErrorMessages(error, showMessage);
      },
    }),
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        gcTime: 10 * 60 * 1000,
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  });
  return queryClient;
}

const QueryProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const { showMessage } = useSnackbar();
  const [queryClient] = useState(() => createQueryClient(showMessage));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

export const Providers: FC<ProvidersProps> = ({ children }) => {
  return (
    <MuiThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <SnackbarProvider>
          <QueryProvider>
            <ConfirmationDialogProvider>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <CssBaseline />
                <ProgramProvider>{children}</ProgramProvider>
              </LocalizationProvider>
            </ConfirmationDialogProvider>
          </QueryProvider>
        </SnackbarProvider>
      </StyledThemeProvider>
    </MuiThemeProvider>
  );
};
