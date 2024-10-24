import { Box } from '@mui/material';
import * as React from 'react';
import styled from 'styled-components';

const StyledGreyBox = styled(Box)`
  background-color: #fafafa;
  width: 100%;
`;

export function GreyBox({
  children,
  ...props
}: React.PropsWithChildren<
React.ComponentProps<typeof Box>
>): React.ReactElement {
  return <StyledGreyBox {...props}>{children}</StyledGreyBox>;
}
