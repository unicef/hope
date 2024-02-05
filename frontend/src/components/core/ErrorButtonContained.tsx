import React from 'react';
import { Button } from '@mui/material';
import { styled } from '@mui/system';

const ErrorButton = styled(Button)({
  backgroundColor: '#C21313',
  color: 'white',
  '&:hover': {
    backgroundColor: '#9f1010',
  },
});

export const ErrorButtonContained = ({
  children,
  ...otherProps
}): React.ReactElement => {
  return (
    <ErrorButton variant='contained' {...otherProps}>
      {children}
    </ErrorButton>
  );
};
