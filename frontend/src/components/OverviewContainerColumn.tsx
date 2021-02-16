import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  align-items: center;
  flex-direction: column;
`;

export function OverviewContainerColumn({ children }): React.ReactElement {
  return <Container>{children}</Container>;
}
