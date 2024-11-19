import { red } from '@mui/material/colors';
import { createTheme } from '@mui/material/styles';
import { css } from 'styled-components';
import { DARK_GRAY, NAVY_BLUE } from './config/colors';

// A custom theme for this app
const muiTheme = createTheme({
  spacing: (factor) => factor * 4,
  palette: {
    primary: {
      main: NAVY_BLUE,
    },
    secondary: {
      main: DARK_GRAY,
    },
    error: {
      main: red['600'],
    },
    background: {
      default: '#EEEEEE',
    },
  },
  typography: {
    h6: {
      fontSize: '20px',
      fontWeight: 400,
    },
  },
});

export const FONT = 'Roboto';
export const theme = {
  ...muiTheme,
  spacing: muiTheme.spacing,
  drawer: {
    width: 270,
  },
  hctPalette: {
    orange: '#FC942A',
    blue: '#D8E1EE',
    darkerBlue: '#033D90',
    green: '#10CB16',
    gray: '#4E606A',
    lightGray: '#d8d8d8',
    lighterGray: '#e4e4e4',
    lightestGray: '#fafafa',
    red: '#EF4343',
    brown: '#D9D1CE',
    darkBrown: '#715247',
    navyBlue: '#003C8F',
    lightBlue: '#00ADEF',
  },
  hctTypography: {
    fontFamily: FONT,
    font: {
      fontFamily: FONT,
    },
    label: {
      color: 'rgba(37,59,70,0.6)',
      fontFamily: FONT,
      fontSize: '11px',
      fontWeight: 500,
      letterSpacing: '0.39px',
      lineHeight: '16px',
      textTransform: 'uppercase',
    },
  },
  styledMixins: {
    label: css`
      color: rgba(37, 59, 70, 0.6);
      font-family: ${FONT};
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.39px;
      line-height: 16px;
      text-transform: uppercase;
    `,
  },
};

export type MiśTheme = typeof theme;
