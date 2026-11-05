import { Box } from '@mui/material';
import type { BoxProps } from '@mui/material';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

export const DialogContainer = (props: BoxProps): ReactElement => (
  <Box sx={{ width: responsiveValue('100%', '700px') }} {...props} />
);
