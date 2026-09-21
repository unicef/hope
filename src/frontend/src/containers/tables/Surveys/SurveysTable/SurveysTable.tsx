import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { dateToIsoString } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { headCells } from './SurveysTableHeadCells';
import { SurveysTableRow } from './SurveysTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import type { PaginatedSurveyList } from '@restgenerated/models/PaginatedSurveyList';
import type { Survey } from '@restgenerated/models/Survey';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface SurveysTableProps {
  filter;
  canViewDetails: boolean;
}

function SurveysTable({
  filter,
  canViewDetails,
}: SurveysTableProps): ReactElement {
  const { programId, baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const businessAreaSlug = baseUrl.split('/')[0];

  const filterVariables = useMemo(
    () => ({
      businessAreaSlug,
      programCode: programId,
      search: filter.search,
      paymentPlan: filter.targetPopulation || '',
      createdBy: filter.createdBy || '',
      createdAtRange: JSON.stringify({
        min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
        max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      }),
    }),
    [
      businessAreaSlug,
      programId,
      filter.search,
      filter.targetPopulation,
      filter.createdBy,
      filter.createdAtRangeMin,
      filter.createdAtRangeMax,
    ],
  );

  const table = useTableState({
    initialRowsPerPage: 10,
    defaultOrderBy: 'created_at',
    defaultOrderDirection: 'desc',
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const surveysListParams = createApiParams(
    { businessAreaSlug, programCode: programId },
    { ...filterVariables, ...table.paginationParams },
  );
  const surveysCountParams = createApiParams(
    { businessAreaSlug, programCode: programId },
    filterVariables,
  );

  const {
    data: dataSurveys,
    isLoading: isLoadingSurveys,
    isFetching: isFetchingSurveys,
    error: errorSurveys,
  } = useQuery<PaginatedSurveyList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsSurveysList,
      surveysListParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysList(surveysListParams),
    placeholderData: keepPreviousData,
    enabled: !!businessAreaSlug && !!programId,
  });

  const { data: dataSurveysCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsSurveysCountRetrieve,
      surveysCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysCountRetrieve(
        surveysCountParams,
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, dataSurveysCount);

  return (
    <TableWrapper>
      <UniversalRestTable
        headCells={headCells}
        title={t('Surveys List')}
        data={dataSurveys}
        isLoading={isLoadingSurveys}
        isFetching={isFetchingSurveys}
        error={errorSurveys}
        tableState={table}
        itemsCount={itemsCount}
        renderRow={(row: Survey) => (
          <SurveysTableRow
            key={row.id}
            survey={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(SurveysTable, 'SurveysTable');
