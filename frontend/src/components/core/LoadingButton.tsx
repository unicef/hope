import { Button, CircularProgress } from '@material-ui/core';
import React from 'react';

export const LoadingButton = ({
  loading,
  children,
  ...otherProps
}): React.ReactElement => {
  return (
    <Button
      {...otherProps}
      disabled={otherProps.disabled || loading}
      endIcon={loading ? <CircularProgress color='inherit' size={20} /> : null}
    >
      {children}
    </Button>
  );
};
