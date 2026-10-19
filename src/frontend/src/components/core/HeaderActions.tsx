import { Box } from '@mui/material';
import type { ReactElement, ReactNode } from 'react';
import { responsiveValue } from 'src/responsive';

interface HeaderActionsProps {
  children: ReactNode;
  /**
   * Desktop spacing: `around` puts a margin on every side of each action,
   * `between` puts a gap between actions and a vertical margin on the row.
   */
  spacing?: 'around' | 'between';
}

/** Page header action buttons: a row on desktop, full-width buttons stacked one per line on mobile. */
export function HeaderActions({
  children,
  spacing = 'around',
}: HeaderActionsProps): ReactElement {
  const between = spacing === 'between';
  return (
    <Box
      data-cy="header-actions"
      sx={{
        display: 'flex',
        flexDirection: responsiveValue('column', 'row'),
        alignItems: responsiveValue('stretch', 'center'),
        gap: responsiveValue(2, between ? 2 : 0),
        my: responsiveValue(0, between ? 2 : 0),
        width: responsiveValue('100%', 'auto'),
        '& > *': { m: responsiveValue(0, between ? 0 : 2) },
        '& .MuiButton-root': { width: responsiveValue('100%', 'auto') },
      }}
    >
      {children}
    </Box>
  );
}
