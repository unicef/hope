import React from 'react';
import { Dialog as MuiDialog } from '@mui/material';

export function Dialog(props): React.ReactElement {
  return <MuiDialog data-cy="dialog-root" {...props} />;
}
