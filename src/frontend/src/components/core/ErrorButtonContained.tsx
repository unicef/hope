import { Button } from '@mui/material';
import { styled } from '@mui/system';
import { ReactElement } from 'react';

const ErrorButton = styled(Button)({
  backgroundColor: '#C21313',
  color: 'white',
  '&:hover': {
    backgroundColor: '#9f1010',
  },
});

export function ErrorButtonContained({
  children,
  ...otherProps
}): ReactElement {
  return (
    <ErrorButton variant="contained" {...otherProps}>
      {children}
    </ErrorButton>
  );
}
