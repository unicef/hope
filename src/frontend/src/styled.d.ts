// import original module declarations
import 'styled-components';
import { Theme as MuiTheme } from '@mui/material/styles';

// extend the module declarations
declare module 'styled-components' {
  export interface DefaultTheme extends MuiTheme {
    hctPalette: {
      orange: string;
      blue: string;
      darkerBlue: string;
      green: string;
      gray: string;
      lightGray: string;
      lighterGray: string;
      lightestGray: string;
      red: string;
      brown: string;
      darkBrown: string;
      navyBlue: string;
      lightBlue: string;
    };
    hctTypography: {
      fontFamily: string;
      font: {
        fontFamily: string;
      };
      label: {
        color: string;
        fontFamily: string;
        fontSize: string;
        fontWeight: number;
        letterSpacing: string;
        lineHeight: string;
        textTransform: string;
      };
    };
    drawer: {
      width: number;
    };
    styledMixins: any;
  }
}
