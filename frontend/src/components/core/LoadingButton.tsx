import { Button, CircularProgress } from '@mui/material';
import * as React from 'react';

export function LoadingButton({
  loading,
  children,
  ...otherProps
}): React.ReactElement {
  return (
    <Button
      {...otherProps}
      disabled={otherProps.disabled || loading}
      endIcon={loading ? <CircularProgress color="inherit" size={20} /> : null}
    >
      {children}
    </Button>
  );
}
