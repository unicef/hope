import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsForTableQuery,
  AllProgramsForTableQueryVariables,
  ProgrammeChoiceDataQuery,
  useAllProgramsForTableQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './ProgrammesHeadCells';
import withErrorBoundary from '@components/core/withErrorBoundary';
import ProgrammesTableRow from './ProgrammesTableRow';

interface ProgrammesTableProps {
  businessArea: string;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}

function ProgrammesTable({
  businessArea,
  filter,
  choicesData,
}: ProgrammesTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables: AllProgramsForTableQueryVariables = {
    businessArea,
    search: filter.search,
    startDate: filter.startDate || null,
    endDate: filter.endDate || null,
    status: filter.status,
    sector: filter.sector,
    numberOfHouseholds: JSON.stringify({
      min: filter.numberOfHouseholdsMin,
      max: filter.numberOfHouseholdsMax,
    }),
    budget: JSON.stringify({ min: filter.budgetMin, max: filter.budgetMax }),
    dataCollectingType: filter.dataCollectingType,
  };
  return (
    <>
      <TableWrapper>
        <UniversalTable<
          AllProgramsForTableQuery['allPrograms']['edges'][number]['node'],
          AllProgramsForTableQueryVariables
        >
          title={t('Programmes')}
          headCells={headCells}
          query={useAllProgramsForTableQuery}
          queriedObjectName="allPrograms"
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
    </>
  );
}
export default withErrorBoundary(ProgrammesTable, 'ProgrammesTable');
