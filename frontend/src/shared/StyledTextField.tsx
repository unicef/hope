import { TextField } from '@mui/material';
import * as React from 'react';

export function StyledTextField({ ...props }): React.ReactElement {
  return <TextField {...props} variant="outlined" size="small" />;
}
