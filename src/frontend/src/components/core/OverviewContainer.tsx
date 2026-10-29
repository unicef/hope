import { Box } from '@mui/material';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

export function OverviewContainer({ children }): ReactElement {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: responsiveValue('column', 'row'),
        alignItems: responsiveValue('stretch', 'center'),
      }}
    >
      {children}
    </Box>
  );
}
