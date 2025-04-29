import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { ProgrammeChoiceDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './ProgrammesHeadCells';
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
  const { programId, isAllPrograms } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      beneficiaryGroupMatch: isAllPrograms ? '' : programId,
      compatibleDct: isAllPrograms ? '' : programId,
      search: filter.search,
      startDate: filter.startDate || null,
      endDate: filter.endDate || null,
      status: filter.status,
      sector: filter.sector,
      numberOfHouseholds: JSON.stringify({
        before: filter.numberOfHouseholdsMin,
        after: filter.numberOfHouseholdsMax,
      }),
      budget: JSON.stringify({ min: filter.budgetMin, max: filter.budgetMax }),
      dataCollectingType: filter.dataCollectingType,
      ordering: 'startDate',
    }),
    [
      businessArea,
      programId,
      isAllPrograms,
      filter.search,
      filter.startDate,
      filter.endDate,
      filter.status,
      filter.sector,
      filter.numberOfHouseholdsMin,
      filter.numberOfHouseholdsMax,
      filter.budgetMin,
      filter.budgetMax,
      filter.dataCollectingType,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: dataPrograms,
    isLoading: isLoadingPrograms,
    error: errorPrograms,
  } = useQuery<PaginatedProgramListList>({
    queryKey: ['businessAreasProgramsList', initialQueryVariables],
    queryFn: () =>
      RestService.restBusinessAreasProgramsList(initialQueryVariables),
    enabled: !!initialQueryVariables.businessAreaSlug,
  });

  const { data: dataProgramsCount } = useQuery<CountResponse>({
    queryKey: ['businessAreasProgramsCount', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsCountRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  return (
    <>
      <TableWrapper>
        <UniversalRestTable
          title={t('Programmes')}
          headCells={headCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          defaultOrderBy="startDate"
          data={dataPrograms}
          isLoading={isLoadingPrograms}
          error={errorPrograms}
          itemsCount={dataProgramsCount?.count}
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
