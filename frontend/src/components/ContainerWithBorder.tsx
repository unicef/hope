import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

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
  return <Container>{children}</Container>;
}
