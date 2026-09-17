import { DialogActions as MuiDialogActions } from '@mui/material';
import type { ReactElement } from 'react';

export function DialogActions(props): ReactElement {
  return <MuiDialogActions data-cy="dialog-actions-container" {...props} />;
}
