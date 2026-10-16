import { Paper } from '@mui/material';
import type { ReactNode, ReactElement } from 'react';
import styled from 'styled-components';
import { responsiveValue } from 'src/responsive';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  flex-direction: column;
  && > div {
    margin: 5px;
  }
`;
interface ContainerColumnWithBorderProps {
  children: ReactNode;
  column?: boolean;
}
export function ContainerColumnWithBorder({
  children,
}: ContainerColumnWithBorderProps): ReactElement {
  return (
    <Container sx={{ padding: responsiveValue('16px', '32px 44px') }}>
      {children}
    </Container>
  );
}
