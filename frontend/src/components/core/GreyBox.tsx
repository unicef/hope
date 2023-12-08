import { Box } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

const StyledGreyBox = styled(Box)`
  background-color: #fafafa;
  width: 100%;
`;

export const GreyBox = ({
  children,
  ...props
}: React.PropsWithChildren<
React.ComponentProps<typeof Box>
>): React.ReactElement =>  {
  return <StyledGreyBox {...props}>{children}</StyledGreyBox>;
};
