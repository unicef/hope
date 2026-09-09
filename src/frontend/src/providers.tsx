import {
  MutationCache,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { isStaticReferenceQuery } from '@utils/queryCacheUtils';
import { CssBaseline } from '@mui/material';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import type { FC, ReactNode } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { ConfirmationDialogProvider } from '@core/ConfirmationDialog';
import { theme } from './theme';
import { ProgramProvider } from './programContext';
import { SnackbarProvider } from '@hooks/useSnackBar';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface ProvidersProps {
  children: ReactNode[];
}

// Safety net for eventual freshness only: `refetchType: 'none'` marks queries stale without
// refetching, so it never re-fires a GET on a just-deleted resource. Targeted per-flow
// invalidations still do the immediate on-screen refresh.
const queryClient: QueryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => !isStaticReferenceQuery(query.queryKey),
        refetchType: 'none',
      });
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

export const Providers: FC<ProvidersProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <MuiThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <ConfirmationDialogProvider>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <CssBaseline />
              <ProgramProvider>
                <SnackbarProvider>{children}</SnackbarProvider>
              </ProgramProvider>
            </LocalizationProvider>
          </ConfirmationDialogProvider>
        </StyledThemeProvider>
      </MuiThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};
