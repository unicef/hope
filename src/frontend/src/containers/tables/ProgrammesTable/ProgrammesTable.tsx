import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { createApiParams } from '@utils/apiUtils';
import { restQueryKey } from '@utils/queryKeys';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTranslation } from 'react-i18next';
import { headCells } from './ProgrammesHeadCells';
import ProgrammesTableRow from './ProgrammesTableRow';
import type { ProgramList } from '@restgenerated/models/ProgramList';

interface ProgrammesTableProps {
  businessArea: string;
  filter;
  choicesData: ProgramChoices;
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
      beneficiaryGroupMatch: isAllPrograms ? '' : programId,
      compatibleDct: isAllPrograms ? '' : programId,
      search: filter.search,
      startDate: filter.startDate || null,
      endDate: filter.endDate || null,
      status: filter.status !== '' ? filter.status : undefined,
      sector: filter.sector,
      numberOfHouseholdsMax: filter.numberOfHouseholdsMax,
      numberOfHouseholdsMin: filter.numberOfHouseholdsMin,
      budgetMax: filter.budgetMax,
      budgetMin: filter.budgetMin,
      dataCollectingType: filter.dataCollectingType,
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
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [page, setPage] = useState(0);

  const programsListParams = createApiParams(
    { businessAreaSlug: businessArea },
    queryVariables,
    { withPagination: true },
  );
  const {
    data: dataPrograms,
    isLoading: isLoadingPrograms,
    isFetching: isFetchingPrograms,
    error: errorPrograms,
  } = useQuery<PaginatedProgramListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsList,
      programsListParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsList(programsListParams),
    placeholderData: keepPreviousData,
    enabled: !!queryVariables.businessAreaSlug,
  });

  const programsCountParams = createApiParams(
    { businessAreaSlug: businessArea },
    queryVariables,
  );
  const { data: dataProgramsCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsCountRetrieve,
      programsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsCountRetrieve(programsCountParams),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, dataProgramsCount);

  return (
    <>
      <TableWrapper>
        <UniversalRestTable
          title={t('Programmes')}
          headCells={headCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          data={dataPrograms}
          isLoading={isLoadingPrograms}
          isFetching={isFetchingPrograms}
          error={errorPrograms}
          itemsCount={itemsCount}
          renderRow={(row: ProgramList) => (
            <ProgrammesTableRow
              key={row.id}
              program={row}
              choicesData={choicesData}
            />
          )}
          page={page}
          setPage={setPage}
        />
      </TableWrapper>
    </>
  );
}
export default withErrorBoundary(ProgrammesTable, 'ProgrammesTable');
