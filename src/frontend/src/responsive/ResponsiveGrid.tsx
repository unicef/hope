import { Grid } from '@mui/material';
import type { GridProps } from '@mui/material';
import type { ReactElement } from 'react';
import { responsiveValue } from './breakpoints';
import type { ResponsiveValue } from './breakpoints';

export type ResponsiveGridSize =
  'full' | 'half' | 'third' | 'quarter' | 'sixth';

const COLUMNS: Record<ResponsiveGridSize, number> = {
  full: 12,
  half: 6,
  third: 4,
  quarter: 3,
  sixth: 2,
};

export const responsiveGridSize = (
  size: ResponsiveGridSize,
  mobileSize: ResponsiveGridSize = 'full',
): ResponsiveValue<number> =>
  responsiveValue(COLUMNS[mobileSize], COLUMNS[size]);

interface ResponsiveGridProps extends Omit<GridProps, 'size' | 'container'> {
  size: ResponsiveGridSize;
  /** Width on mobile; full width unless fields should share a row, like From/To pairs. */
  mobileSize?: ResponsiveGridSize;
}

/** Grid item: `mobileSize` (default full width) on mobile, `size` of the row on desktop. */
export const ResponsiveGrid = ({
  size,
  mobileSize,
  ...props
}: ResponsiveGridProps): ReactElement => (
  <Grid size={responsiveGridSize(size, mobileSize)} {...props} />
);

interface ResponsiveGridContainerProps extends Omit<
  GridProps,
  'container' | 'spacing'
> {
  spacing: number;
  mobileSpacing?: number;
}

/**
 * Grid container whose spacing shrinks on mobile, where items stack and
 * desktop-sized gaps between every field become excessive.
 */
export const ResponsiveGridContainer = ({
  spacing,
  mobileSpacing = Math.min(spacing, 3),
  ...props
}: ResponsiveGridContainerProps): ReactElement => (
  <Grid
    container
    spacing={responsiveValue(mobileSpacing, spacing)}
    {...props}
  />
);
