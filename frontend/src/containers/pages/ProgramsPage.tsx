import React from 'react';
import styled from 'styled-components';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import { ProgramNode, useAllProgramsQuery } from '../../__generated__/graphql';
import { CreateProgram } from '../dialogs/programs/CreateProgram';
import { getCurrentLocation } from '../../utils/utils';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
  justify-content: center;
`;
export function ProgramsPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { data } = useAllProgramsQuery({
    variables: {
      businessArea,
    },
  });

  const toolbar = (
    <PageHeader title='Programme Management'>
      <CreateProgram />
    </PageHeader>
  );

  if (!data || !data.allPrograms) {
    return <div>{toolbar}</div>;
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
