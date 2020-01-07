import { red } from '@material-ui/core/colors';
import { createMuiTheme, Theme } from '@material-ui/core/styles';
import { DARK_GRAY, NAVY_BLUE } from './config/colors';
import { css } from 'styled-components';

// A custom theme for this app
const muiTheme = createMuiTheme({
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
console.log('tpppp', theme.mixins.toolbar);
export type MiśTheme = typeof theme;
