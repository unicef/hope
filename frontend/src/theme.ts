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
    width: 260,
  },
};

export interface MiśTheme extends Theme {
  drawer: {
    width: number;
  };
}
