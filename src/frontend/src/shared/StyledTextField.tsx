import { TextField } from '@mui/material';
import type { ReactElement } from 'react';

export const StyledTextField = ({ ...props }): ReactElement => {
  return <TextField {...props} variant="outlined" size="small" />;
};
