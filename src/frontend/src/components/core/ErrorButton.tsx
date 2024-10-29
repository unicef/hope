import { styled } from '@mui/system';
import Button from '@mui/material/Button';
import { ReactElement } from 'react';

const ErrorStyledButton = styled(Button)`
  color: #c21313;
`;

export function ErrorButton({ children, ...otherProps }): ReactElement {
  return <ErrorStyledButton {...otherProps}>{children}</ErrorStyledButton>;
}
