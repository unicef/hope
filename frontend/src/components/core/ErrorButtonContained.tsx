import React from 'react';
import { makeStyles } from '@mui/material/styles';
import Button from '@mui/material/Button';

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
