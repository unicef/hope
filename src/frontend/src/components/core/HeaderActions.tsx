import { Box } from '@mui/material';
import type { ReactElement, ReactNode } from 'react';
import { responsiveValue } from 'src/responsive';

/** Page header action buttons: a row on desktop, full-width buttons stacked one per line on mobile. */
export function HeaderActions({
  children,
}: {
  children: ReactNode;
}): ReactElement {
  return (
    <Box
      data-cy="header-actions"
      sx={{
        display: 'flex',
        flexDirection: responsiveValue('column', 'row'),
        alignItems: responsiveValue('stretch', 'center'),
        gap: responsiveValue(2, 0),
        width: responsiveValue('100%', 'auto'),
        '& > *': { m: responsiveValue(0, 2) },
        '& .MuiButton-root': { width: responsiveValue('100%', 'auto') },
      }}
    >
      {children}
    </Box>
  );
}
