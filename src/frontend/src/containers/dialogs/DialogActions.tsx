import { DialogActions as MuiDialogActions } from '@mui/material';
import { ReactElement } from 'react';

export function DialogActions(props): ReactElement {
  return <MuiDialogActions data-cy="dialog-actions-container" {...props} />;
}
