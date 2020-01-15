import React from 'react';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import { Programme } from '../Dialogs/Programme/Programme';
import { Container } from '@material-ui/core';
import styled from 'styled-components';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
`;

export function ProgramsPage() {
  return (
    <div>
      <PageHeader title='Programme Management'>
        <Programme />
      </PageHeader>
      <Container>
        <PageContainer>
          <ProgramCard />
          <ProgramCard />
          <ProgramCard />
          <ProgramCard />
        </PageContainer>
      </Container>
    </div>
  );
}
