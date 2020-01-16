import React from 'react';
import { Button } from '@material-ui/core';
import styled from 'styled-components';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import { ProgramNode, useAllProgramsQuery } from '../../__generated__/graphql';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
  justify-content: center;
`;
export function ProgramsPage(): React.ReactElement {
  const {  data } = useAllProgramsQuery();

  const toolbar = (
    <PageHeader title='Programme Management'>
      <Button variant='contained' color='primary'>
        NEW PROGRAMME
      </Button>
    </PageHeader>
  );

  if (!data || !data.allPrograms) {
    return (
      <div>
        {toolbar}
      </div>
    );
  }
  const programsList = data.allPrograms.edges.map((node) => {
    const program = node.node as ProgramNode;
    return <ProgramCard key={program.id} program={program} />;
  });
  return (
    <div>
      {toolbar}
      <PageContainer>{programsList}</PageContainer>
    </div>
  );
}
