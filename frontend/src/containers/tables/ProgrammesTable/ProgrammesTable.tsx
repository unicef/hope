import React, { ReactElement } from 'react';
import styled from 'styled-components';
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
  businessArea: string;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}

export function ProgrammesTable({
  businessArea,
  filter,
  choicesData,
}: ProgrammesTableProps): ReactElement {
  const initialVariables: AllProgramsQueryVariables = {
    businessArea,
    search: filter.search,
    startDate: filter.startDate,
    endDate: filter.endDate,
    status: filter.status,
    sector: filter.sector,
    numberOfHouseholds: JSON.stringify(filter.numberOfHouseholds),
    budget: JSON.stringify(filter.budget),
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
