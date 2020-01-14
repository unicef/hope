import React from 'react';
import Container from '@material-ui/core/Container';
import { Button } from '@material-ui/core';
import styled from 'styled-components';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import { allProgramsQuery } from '../../relay/queries/allProgramsQuery';
import { AllProgramsQuery } from '../../__generated__/AllProgramsQuery.graphql';
import { useQuery } from 'relay-hooks/lib';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
  justify-content: center;
`;
export function ProgramsPage(): React.ReactElement {
  const { props, error, retry, cached } = useQuery<AllProgramsQuery>(
    allProgramsQuery,
    {},
    {},
  );
  const toolbar = (
    <PageHeader title='Programme Management'>
      <Button variant='contained' color='primary'>
        NEW PROGRAMME
      </Button>
    </PageHeader>
  );

  if (!props || !props.allPrograms) {
    return (
      <div>
        {toolbar}
      </div>
    );
  }
  console.log('all', props);
  const programsList = props.allPrograms.edges.map((node) => {
    const program = node.node;
    return <ProgramCard key={program.id} program={program} />;
  });
  return (
    <div>
      {toolbar}
      <PageContainer>{programsList}</PageContainer>
    </div>
  );
}
