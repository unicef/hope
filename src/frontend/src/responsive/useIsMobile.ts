import useMediaQuery from '@mui/material/useMediaQuery';
import { theme } from 'src/theme';
import { MOBILE_BREAKPOINT } from './breakpoints';

/**
 * Only for structural switches that need different markup (drawer variant,
 * overflow menus, vertical stepper). Spacing and column widths belong in
 * `responsiveValue` / `ResponsiveGrid` instead.
 */
export const useIsMobile = (): boolean =>
  useMediaQuery(theme.breakpoints.down(MOBILE_BREAKPOINT), { noSsr: true });
