import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import type { MessageList } from '@restgenerated/models/MessageList';
import type { PaginatedMessageListList } from '@restgenerated/models/PaginatedMessageListList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { dateToIsoString } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { headCells } from './CommunicationTableHeadCells';
import { CommunicationTableRow } from './CommunicationTableRow';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface CommunicationTableProps {
  filter;
  canViewDetails: boolean;
}

function CommunicationTable({
  filter,
  canViewDetails,
}: CommunicationTableProps): ReactElement {
  const { programId, businessArea } = useBaseUrl();
  const { t } = useTranslation();

  const initialQueryVariables = useMemo(() => {
    return {
      businessAreaSlug: businessArea,
      programSlug: programId,
      createdAtRange: JSON.stringify({
        min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
        max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      }),
      paymentPlan: filter.targetPopulation,
      createdBy: filter.createdBy || undefined,
    };
  }, [
    businessArea,
    programId,
    filter.createdAtRangeMin,
    filter.createdAtRangeMax,
    filter.targetPopulation,
    filter.createdBy,
  ]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery<PaginatedMessageListList>({
    queryKey: [
      'businessAreasProgramsMessagesList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsMessagesList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
  });

  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsMessagesCount',
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsMessagesCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
  });

  const renderRow = (message: MessageList): ReactElement => (
    <CommunicationTableRow
      key={message.id}
      message={message}
      canViewDetails={canViewDetails}
    />
  );

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('Messages List')}
        renderRow={renderRow}
        headCells={headCells}
        data={data}
        error={error}
        isLoading={isLoading}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={countData?.count}
        initialRowsPerPage={10}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(CommunicationTable, 'CommunicationTable');
