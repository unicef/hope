import { Button, CircularProgress } from '@material-ui/core';
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
  error: {
    color: '#fff',
    backgroundColor: '#C21313',
  },
});

export const LoadingButton = ({
  loading,
  children,
  error = false,
  endIcon = null,
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles(otherProps);

  return (
    <Button
      {...otherProps}
      disabled={otherProps.disabled || loading}
      endIcon={
        loading ? <CircularProgress color='inherit' size={20} /> : endIcon
      }
      className={error ? classes.error : null}
    >
      {children}
    </Button>
  );
};
