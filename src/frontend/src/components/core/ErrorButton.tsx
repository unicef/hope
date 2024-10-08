import * as React from 'react';
import { styled } from '@mui/system';
import Button from '@mui/material/Button';

const ErrorStyledButton = styled(Button)`
  color: #c21313;
`;

export function ErrorButton({ children, ...otherProps }): React.ReactElement {
  return <ErrorStyledButton {...otherProps}>{children}</ErrorStyledButton>;
}
