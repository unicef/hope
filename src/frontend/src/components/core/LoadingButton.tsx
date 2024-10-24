import { Button, CircularProgress } from '@mui/material';
import { ReactElement } from 'react';

export function LoadingButton({
  loading,
  children,
  ...otherProps
}): ReactElement {
  return (
    <Button
      {...otherProps}
      disabled={otherProps.disabled || loading}
      endIcon={
        loading ? (
          <CircularProgress color="inherit" size={20} />
        ) : (
          otherProps.endIcon
        )
      }
    >
      {children}
    </Button>
  );
}
