import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import type { MessageList } from '@restgenerated/models/MessageList';
import type { PaginatedMessageListList } from '@restgenerated/models/PaginatedMessageListList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { dateToIsoString } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { headCells } from './CommunicationTableHeadCells';
import { CommunicationTableRow } from './CommunicationTableRow';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { usePersistedCount } from '@hooks/usePersistedCount';

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

  const filterVariables = useMemo(() => {
    return {
      businessAreaSlug: businessArea,
      programCode: programId,
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

  const table = useTableState({
    initialRowsPerPage: 10,
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const messagesListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    { ...filterVariables, ...table.paginationParams },
  );
  const messagesCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );

  const { data, isLoading, isFetching, error } =
    useQuery<PaginatedMessageListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsMessagesList,
        messagesListParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsMessagesList(messagesListParams),
      placeholderData: keepPreviousData,
    });

  const { data: countData } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsMessagesCountRetrieve,
      messagesCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsMessagesCountRetrieve(
        messagesCountParams,
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  const renderRow = (message: MessageList): ReactElement => (
    <CommunicationTableRow
      key={message.id}
      message={message}
      canViewDetails={canViewDetails}
    />
  );
  const itemsCount = usePersistedCount(page, countData);

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('Messages List')}
        renderRow={renderRow}
        headCells={headCells}
        data={data}
        error={error}
        isLoading={isLoading}
        isFetching={isFetching}
        tableState={table}
        itemsCount={itemsCount}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(CommunicationTable, 'CommunicationTable');
