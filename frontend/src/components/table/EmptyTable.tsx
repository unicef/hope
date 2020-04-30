import React from 'react';
import { Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  text-align: center;
`;

export function EmptyTable() {
  return (
    <PaperContainer>
      <Typography variant='h6'>
        No data
        </Typography>
    </PaperContainer>
  )
}