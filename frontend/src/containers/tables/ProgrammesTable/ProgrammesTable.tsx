import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '../../../components/core/TableWrapper';
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
  const { t } = useTranslation();
  const initialVariables: AllProgramsQueryVariables = {
    businessArea,
    search: filter.search,
    startDate: filter.startDate,
    endDate: filter.endDate,
    status: filter.status,
    sector: filter.sector,
    numberOfHouseholds: JSON.stringify({
      min: filter.numberOfHouseholdsMin,
      max: filter.numberOfHouseholdsMax,
    }),
    budget: JSON.stringify({ min: filter.budgetMin, max: filter.budgetMax }),
  };
  return (
    <TableWrapper>
      <UniversalTable<ProgramNode, AllProgramsQueryVariables>
        title={t('Programmes')}
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
