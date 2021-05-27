import {Paper} from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  && > div {
    margin: 5px;
  }
`;
interface ContainerColumnWithBorderProps {
  children: React.ReactNode;
  column?: boolean;
}
export function ContainerColumnWithBorder({
  children,
}: ContainerColumnWithBorderProps): React.ReactElement {
  return <Container>{children}</Container>;
}
