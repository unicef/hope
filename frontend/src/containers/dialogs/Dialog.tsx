import React from 'react';
import { Dialog as MuiDialog } from '@mui/material';

export const Dialog = (props): React.ReactElement => (
  <MuiDialog data-cy="dialog-root" {...props} />
);
