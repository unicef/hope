import { Box } from '@mui/material';
import type { ReactElement, ReactNode } from 'react';
import { MOBILE_BREAKPOINT, responsiveValue } from 'src/responsive';

interface HeaderActionsProps {
  children: ReactNode;
  /**
   * Desktop spacing: `around` puts a margin on every side of each action,
   * `between` puts a gap between actions and a vertical margin on the row,
   * `gap` only puts a gap between actions, `none` keeps the actions' own margins.
   */
  spacing?: 'around' | 'between' | 'gap' | 'none';
}

/** Page header action buttons: a row on desktop, full-width buttons stacked one per line on mobile. */
export function HeaderActions({
  children,
  spacing = 'around',
}: HeaderActionsProps): ReactElement {
  const between = spacing === 'between';
  const gap = between || spacing === 'gap';
  return (
    <Box
      data-cy="header-actions"
      sx={(theme) => ({
        display: 'flex',
        flexDirection: responsiveValue('column', 'row'),
        alignItems: responsiveValue('stretch', 'center'),
        gap: responsiveValue(2, gap ? 2 : 0),
        my: responsiveValue(0, between ? 2 : 0),
        width: responsiveValue('100%', 'auto'),
        ...(spacing === 'none'
          ? {
              // Doubled class so it beats the margins the actions set in their own `sx`.
              [theme.breakpoints.down(MOBILE_BREAKPOINT)]: {
                '&& > *': { m: 0 },
              },
            }
          : { '& > *': { m: responsiveValue(0, gap ? 0 : 2) } }),
        '& .MuiButton-root': { width: responsiveValue('100%', 'auto') },
      })}
    >
      {children}
    </Box>
  );
}
