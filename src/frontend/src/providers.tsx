import {
  MutationCache,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { isStaticReferenceQuery } from '@utils/queryCacheUtils';
import { CssBaseline } from '@mui/material';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { FC, ReactNode } from 'react';
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

// After ANY successful mutation, invalidate active queries so the UI reflects the write
// immediately (create/edit/status-change etc.). Static reference data (choices, geo areas,
// permissions) is exempt so it keeps its long staleTime. Individual mutations may still add
// their own targeted invalidation; this is the safety net for the app's drifted query keys.
// The onSuccess closure references `queryClient` lazily — it only runs on a mutation success,
// long after the binding is initialised — so the self-reference is safe.
const queryClient: QueryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => !isStaticReferenceQuery(query.queryKey),
      });
    },
  }),
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // Data is considered fresh for 60 seconds
      gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
      retry: 1, // Retry a failed query once (down from the default of 3)
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
