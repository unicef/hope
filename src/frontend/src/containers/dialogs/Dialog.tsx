import { Dialog as MuiDialog } from '@mui/material';
import { ReactElement } from 'react';

export function Dialog(props): ReactElement {
  return <MuiDialog data-cy="dialog-root" {...props} />;
}
