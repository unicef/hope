import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
<<<<<<< HEAD:frontend/src/containers/tables/programs/ProgrammesTable/ProgrammesTable.tsx
import { TableWrapper } from '../../../../components/core/TableWrapper';
=======
>>>>>>> cb4319bb4d0d695656d0ec4956559438fdd72937:frontend/src/containers/tables/ProgrammesTable/ProgrammesTable.tsx
import {
  AllProgramsQuery,
  AllProgramsQueryVariables,
  ProgrammeChoiceDataQuery,
  useAllProgramsQuery,
<<<<<<< HEAD:frontend/src/containers/tables/programs/ProgrammesTable/ProgrammesTable.tsx
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
=======
} from '../../../__generated__/graphql';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { UniversalTable } from '../UniversalTable';
>>>>>>> cb4319bb4d0d695656d0ec4956559438fdd72937:frontend/src/containers/tables/ProgrammesTable/ProgrammesTable.tsx
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
      <UniversalTable<
        AllProgramsQuery['allPrograms']['edges'][number]['node'],
        AllProgramsQueryVariables
      >
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
