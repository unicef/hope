import { ReactElement } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  align-items: center;
  flex-direction: column;
`;

export function OverviewContainerColumn({ children }): ReactElement {
  return <Container>{children}</Container>;
}
