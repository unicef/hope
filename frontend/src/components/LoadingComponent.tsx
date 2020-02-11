import React, { useState } from 'react';
import styled from 'styled-components';
import { CircularProgress } from '@material-ui/core';

const Container = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

interface LoadingComponentProps {
  isLoading?: boolean;
}

export function LoadingComponent({ isLoading = true }) {
  if (!isLoading) {
    return null;
  }
  return (
    <Container>
      <CircularProgress />
    </Container>
  );
}
