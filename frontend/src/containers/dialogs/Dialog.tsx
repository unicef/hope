import React from 'react';
import { Dialog as MuiDialog } from '@material-ui/core';

export const Dialog = (props): React.ReactElement => (
  <MuiDialog data-cy='dialog-root' {...props} />
);
