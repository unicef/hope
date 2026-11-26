import type { Breakpoint } from '@mui/material/styles';

// Below this breakpoint (phones and tablets) the mobile layout is used.
export const MOBILE_BREAKPOINT: Breakpoint = 'lg';

/**
 * Builds a responsive value for `sx` or MUI responsive props, e.g.
 * `sx={{ p: responsiveValue(4, 11) }}`.
 */
export type ResponsiveValue<T> = { xs: T } & Partial<Record<Breakpoint, T>>;

export const responsiveValue = <T>(
  mobile: T,
  desktop: T,
): ResponsiveValue<T> => ({
  xs: mobile,
  [MOBILE_BREAKPOINT]: desktop,
});
