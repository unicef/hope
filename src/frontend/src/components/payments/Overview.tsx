import { Paper } from '@mui/material';
import type { ReactElement, ReactNode } from 'react';
import { SECTION_PADDING, responsiveValue } from 'src/responsive';

export function Overview({ children }: { children: ReactNode }): ReactElement {
  return (
    <Paper sx={{ m: responsiveValue(2, 5), padding: SECTION_PADDING }}>
      {children}
    </Paper>
  );
}
