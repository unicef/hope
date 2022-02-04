import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

export function OverviewContainer({ children }): React.ReactElement {
  return <Container>{children}</Container>;
}
