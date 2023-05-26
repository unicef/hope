import MomentUtils from '@date-io/moment';
import { ThemeProvider } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../theme';
import {ReactFCWithChildren} from "../utils/types";

export const TestProviders: ReactFCWithChildren = ({ children }) => (
  <ThemeProvider theme={theme}>
    <StyledThemeProvider theme={theme}>
      <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
        <CssBaseline />
        {children}
      </MuiPickersUtilsProvider>
    </StyledThemeProvider>
  </ThemeProvider>
);
