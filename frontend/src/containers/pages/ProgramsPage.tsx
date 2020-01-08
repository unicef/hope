import React from 'react';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import Container from '@material-ui/core/Container';
import { Button } from '@material-ui/core';
import styled from 'styled-components';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
`;
const Container1 = styled(Container)`
margin-top: 20px;
`;
export function ProgramsPage() {
  return (
    <div>
      <PageHeader title='Programme Management'>
        <Button variant='contained' color='primary'>
          NEW PROGRAMME
        </Button>
      </PageHeader>
      <Container1>
        <PageContainer>
          <ProgramCard />
          <ProgramCard />
          <ProgramCard />
          <ProgramCard />
        </PageContainer>
      </Container1>
    </div>
  );
}
