import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../theme';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { ReactNode, FC } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

interface TestProvidersProps {
  children: ReactNode;
}

export const TestProviders: FC<TestProvidersProps> = ({ children }) => {
  const queryClient = new QueryClient();

  return (
    <ThemeProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <StyledThemeProvider theme={theme}>
          <LocalizationProvider dateAdapter={AdapterMoment}>
            <CssBaseline />
            {children}
          </LocalizationProvider>
        </StyledThemeProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
};
