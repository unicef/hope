import React from 'react';
import styled from 'styled-components';
import { CircularProgress } from '@material-ui/core';

const Container = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  ${({ absolute }) => (absolute ? 'position: absolute;' : '')}
`;

interface LoadingComponentProps {
  isLoading?: boolean;
  absolute?: boolean;
}

export function LoadingComponent({
  isLoading = true,
  absolute,
}: LoadingComponentProps): React.ReactElement {
  if (!isLoading) {
    return null;
  }
  return (
    <Container absolute={absolute} data-cy='loading-container'>
      <CircularProgress />
    </Container>
  );
}
