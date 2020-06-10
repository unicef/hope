import React from 'react';
import { Dialog as MuiDialog } from '@material-ui/core';

export const Dialog = (props) => (
  <MuiDialog data-cy='dialog-root' {...props} />
);
