import { TextField } from '@mui/material';
import * as React from 'react';

export const StyledTextField = ({ ...props }): React.ReactElement => {
  return <TextField {...props} variant="outlined" size="small" />;
};
