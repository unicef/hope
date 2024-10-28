import { TextField } from '@mui/material';
import { ReactElement } from 'react';

export const StyledTextField = ({ ...props }): ReactElement => {
  return <TextField {...props} variant="outlined" size="small" />;
};
