import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { dateToIsoString, restChoicesToDict } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './SurveysTableHeadCells';
import { SurveysTableRow } from './SurveysTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedSurveyList } from '@restgenerated/models/PaginatedSurveyList';
import { Survey } from '@restgenerated/models/Survey';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { Choice } from '@restgenerated/models/Choice';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface SurveysTableProps {
  filter;
  canViewDetails: boolean;
  choicesData: Array<Choice> | null;
}

function SurveysTable({
  filter,
  canViewDetails,
  choicesData,
}: SurveysTableProps): ReactElement {
  const { programId, baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const businessAreaSlug = baseUrl.split('/')[0];

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug,
      programSlug: programId,
      search: filter.search,
      paymentPlan: filter.targetPopulation || '',
      createdBy: filter.createdBy || '',
      createdAtRange: JSON.stringify({
        min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
        max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      }),
      ordering: '-created_at',
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

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: dataSurveys,
    isLoading: isLoadingSurveys,
    error: errorSurveys,
  } = useQuery<PaginatedSurveyList>({
    queryKey: ['businessAreasProgramsSurveysList', queryVariables],
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysList(
        createApiParams(
          {
            businessAreaSlug: queryVariables.businessAreaSlug,
            programSlug: queryVariables.programSlug,
          },
          queryVariables,
          { withPagination: true },
        ),
      ),
    enabled: !!queryVariables.businessAreaSlug && !!queryVariables.programSlug,
  });

  const { data: dataSurveysCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsSurveysCount',
      businessAreaSlug,
      programId,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysCountRetrieve(
        createApiParams(
          {
            businessAreaSlug: queryVariables.businessAreaSlug,
            programSlug: queryVariables.programSlug,
          },
          queryVariables,
        ),
      ),
    enabled: !!businessAreaSlug && !!programId,
  });

  const categoryDict = restChoicesToDict(choicesData);

  return (
    <TableWrapper>
      <UniversalRestTable
        headCells={headCells}
        title={t('Surveys List')}
        data={dataSurveys}
        isLoading={isLoadingSurveys}
        error={errorSurveys}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        defaultOrderBy="created_at"
        defaultOrderDirection="desc"
        itemsCount={dataSurveysCount?.count}
        initialRowsPerPage={10}
        renderRow={(row: Survey) => (
          <SurveysTableRow
            key={row.id}
            survey={row}
            canViewDetails={canViewDetails}
            categoryDict={categoryDict}
          />
        )}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(SurveysTable, 'SurveysTable');
