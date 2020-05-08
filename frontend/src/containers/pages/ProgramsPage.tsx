import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import {
  ProgramNode,
  useAllProgramsQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { CreateProgram } from '../dialogs/programs/CreateProgram';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
  justify-content: center;
`;
export function ProgramsPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: {
      businessArea,
    },
    fetchPolicy: 'cache-and-network',
  });

  const {
    data: choices,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <CreateProgram />
    </PageHeader>
  );
  if (loading || choicesLoading) {
    return <LoadingComponent />;
  }
  if (!data || !data.allPrograms || !choices) {
    return <div>{toolbar}</div>;
  }
  const programsList = data.allPrograms.edges.map((node) => {
    const program = node.node as ProgramNode;
    return <ProgramCard key={program.id} program={program} choices={choices} />;
  });
  return (
    <div>
      {toolbar}
      <PageContainer data-cy='programs-page-container'>{programsList}</PageContainer>
    </div>
  );
}
