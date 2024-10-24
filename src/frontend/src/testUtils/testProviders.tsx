import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../theme';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { ReactNode, FC } from 'react';

interface TestProvidersProps {
  children: ReactNode;
}

export const TestProviders: FC<TestProvidersProps> = ({ children }) => (
  <ThemeProvider theme={theme}>
    <StyledThemeProvider theme={theme}>
      <LocalizationProvider dateAdapter={AdapterMoment}>
        <CssBaseline />
        {children}
      </LocalizationProvider>
    </StyledThemeProvider>
  </ThemeProvider>
);
