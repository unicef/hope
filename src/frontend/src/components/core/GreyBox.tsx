import { Box } from '@mui/material';
import { PropsWithChildren, ComponentProps, ReactElement } from 'react';
import styled from 'styled-components';

const StyledGreyBox = styled(Box)`
  background-color: #fafafa;
  width: 100%;
`;

export function GreyBox({
  children,
  ...props
}: PropsWithChildren<ComponentProps<typeof Box>>): ReactElement {
  return <StyledGreyBox {...props}>{children}</StyledGreyBox>;
}
