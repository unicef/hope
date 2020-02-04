import { red } from '@material-ui/core/colors';
import { createMuiTheme } from '@material-ui/core/styles';
import { css } from 'styled-components';
import { DARK_GRAY, NAVY_BLUE } from './config/colors';

// A custom theme for this app
const muiTheme = createMuiTheme({
  spacing: 4,
  palette: {
    primary: {
      main: NAVY_BLUE,
    },
    secondary: {
      main: DARK_GRAY,
    },
    error: {
      main: red.A400,
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

const FONT = 'Roboto';
export const theme = {
  ...muiTheme,
  drawer: {
    width: 270,
  },
  hctPalette: {
    oragne: '#FC942A',
    green: '#10CB16',
    gray: '#4E606A',
    lightGray: '#d8d8d8',
    lighterGray: '#e4e4e4',
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
