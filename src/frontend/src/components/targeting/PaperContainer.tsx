import { Paper } from '@mui/material';
import type { PaperProps } from '@mui/material';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

export const PaperContainer = (props: PaperProps): ReactElement => (
  <Paper
    sx={{
      display: 'flex',
      py: 3,
      px: 4,
      m: responsiveValue(2, 5),
      flexDirection: 'column',
      borderBottom: '1px solid rgba(224, 224, 224, 1)',
    }}
    {...props}
  />
);
