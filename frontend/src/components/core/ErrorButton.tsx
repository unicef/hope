import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';

const useStyles = makeStyles({
  error: {
    color: '#C21313',
  },
});

export const ErrorButton = ({
  children,
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles(otherProps);
  return (
    <Button {...otherProps} className={classes.error}>
      {children}
    </Button>
  );
};
