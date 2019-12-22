import { red } from '@material-ui/core/colors';
import { createMuiTheme, Theme } from '@material-ui/core/styles';
import { DARK_GRAY, NAVY_BLUE } from './config/colors';

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
    label: {
      color: 'rgba(37,59,70,0.6)',
      fontFamily: 'Roboto',
      fontSize: '11px',
      fontWeight: 500,
      letterSpacing: '0.39px',
      lineHeight: '16px',
    },
  },
};

export interface MiśTheme extends Theme {
  drawer: {
    width: number;
  };
}
