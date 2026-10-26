import { Box } from '@mui/material';
import type { BoxProps } from '@mui/material';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

export const TableWrapper = (props: BoxProps): ReactElement => (
  <Box sx={{ padding: responsiveValue('8px', '20px') }} {...props} />
);
