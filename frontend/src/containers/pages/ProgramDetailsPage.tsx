import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { ProgramDetails } from '../../components/programs/ProgramDetails';
import { CashPlanTable } from '../CashPlanTable';
import { ProgramNode, useProgramQuery, } from '../../__generated__/graphql';
import { ProgramDetailsPageHeader } from './headers/ProgramDetailsPageHeader';
import { ProgramActivityLogTable } from '../ProgramActivityLogTable';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;

export function ProgramDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data } = useProgramQuery({
    variables: { id },
  });
  if (!data) {
    return null;
  }
  const program = data.program as ProgramNode;
  return (
    <div>
      <ProgramDetailsPageHeader program={program} />
      <Container>
        <ProgramDetails program={program} />
        <TableWrapper>
          <CashPlanTable program={program} />
        </TableWrapper>
        <TableWrapper>
          <ProgramActivityLogTable program={program} />
        </TableWrapper>
      </Container>
    </div>
  );
}
