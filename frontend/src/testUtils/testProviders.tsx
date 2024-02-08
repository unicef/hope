import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import * as React from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../theme';

interface TestProvidersProps {
  children: React.ReactNode;
}

export const TestProviders: React.FC<TestProvidersProps> = ({ children }) => (
  <ThemeProvider theme={theme}>
    <StyledThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </StyledThemeProvider>
  </ThemeProvider>
);
