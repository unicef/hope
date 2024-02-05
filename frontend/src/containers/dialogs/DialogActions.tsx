import React from 'react';
import { DialogActions as MuiDialogActions } from '@mui/material';

export const DialogActions = (props): React.ReactElement => (
  <MuiDialogActions data-cy="dialog-actions-container" {...props} />
);
