import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';

const useStyles = makeStyles({
  error: {
    backgroundColor: '#C21313',
    color: 'white',
  },
});

export const ErrorButtonContained = ({
  children,
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles(otherProps);
  return (
    <Button variant='contained' {...otherProps} className={classes.error}>
      {children}
    </Button>
  );
};
