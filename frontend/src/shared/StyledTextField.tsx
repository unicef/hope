import { TextField } from '@material-ui/core';
import React from 'react';

export const StyledTextField = ({ ...props }): React.ReactElement => {
  return <TextField {...props} variant='outlined' size='small' />;
};
