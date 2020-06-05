import React from 'react';
import { DialogActions as MuiDialogActions } from '@material-ui/core';

export const DialogActions = (props) => (
  <MuiDialogActions data-cy='dialog-actions-container' {...props} />
);
