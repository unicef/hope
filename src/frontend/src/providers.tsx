import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { CssBaseline } from '@mui/material';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { FC, ReactNode } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { ConfirmationDialogProvider } from '@core/ConfirmationDialog';
import { theme } from './theme';
import { ProgramProvider } from './programContext';
import { SnackbarProvider } from '@hooks/useSnackBar';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3';

interface ProvidersProps {
  children: ReactNode[];
}

const queryClient = new QueryClient();

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
