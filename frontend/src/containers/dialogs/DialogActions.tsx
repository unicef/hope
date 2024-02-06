import React from 'react';
import { DialogActions as MuiDialogActions } from '@mui/material';

export function DialogActions(props): React.ReactElement {
  return <MuiDialogActions data-cy="dialog-actions-container" {...props} />;
}
