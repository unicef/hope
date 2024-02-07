import * as React from 'react';
import { makeStyles } from '@mui/material/styles';
import Button from '@mui/material/Button';

const useStyles = makeStyles({
  error: {
    color: '#C21313',
  },
});

export function ErrorButton({ children, ...otherProps }): React.ReactElement {
  const classes = useStyles(otherProps);
  return (
    <Button {...otherProps} className={classes.error}>
      {children}
    </Button>
  );
}
