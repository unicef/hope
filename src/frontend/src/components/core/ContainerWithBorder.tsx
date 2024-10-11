import { Box, Paper } from '@mui/material';
import * as React from 'react';
import styled from 'styled-components';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  flex-direction: row;
  align-items: center;

  && > div {
    margin: 5px;
  }
`;
interface ContainerWithBorderProps {
  children: React.ReactNode;
  column?: boolean;
}
export function ContainerWithBorder({
  children,
}: ContainerWithBorderProps): React.ReactElement {
  return (
    <Container>
      <Box
        style={{ width: '100%' }}
        display="flex"
        flexDirection="column"
        alignItems="flex-end"
      >
        {children}
      </Box>
    </Container>
  );
}
