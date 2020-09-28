import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  AllProgramsQueryVariables,
  ProgrammeChoiceDataQuery,
  ProgramNode,
  useAllProgramsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './ProgrammesHeadCells';
import { ProgrammesTableRow } from './ProgrammesTableRow';

interface ProgrammesTableProps {
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}

export function ProgrammesTable({
  filter,
  choicesData,
}: ProgrammesTableProps): ReactElement {
  const businessArea = useBusinessArea();

  const initialVariables: AllProgramsQueryVariables = {
    businessArea,
    status: filter.status,
  };

  const TableWrapper = styled.div`
    padding: 20px;
  `;
  return (
    <TableWrapper>
      <UniversalTable<ProgramNode, AllProgramsQueryVariables>
        title='Programmes'
        headCells={headCells}
        query={useAllProgramsQuery}
        queriedObjectName='allPrograms'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <ProgrammesTableRow
            key={row.id}
            program={row}
            choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
}
