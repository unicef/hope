import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './TargetPopulationPeopleHeadCells';
import { TargetPopulationPeopleTableRow } from './TargetPopulationPeopleRow';
import { createApiParams } from '@utils/apiUtils';
import type { PaginatedPendingPaymentList } from '@restgenerated/models/PaginatedPendingPaymentList';
import type { PendingPayment } from '@restgenerated/models/PendingPayment';

interface TargetPopulationPeopleTableProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export function TargetPopulationPeopleTable({
  id,
  variables,
  canViewDetails,
}: TargetPopulationPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const filterVariables = useMemo(
    () => ({
      ...variables,
      businessAreaSlug: businessArea,
      programCode: programId,
      targetPopulationId: id,
    }),
    [variables, businessArea, programId, id],
  );
  const table = useTableState({ rowsPerPageOptions: [10, 15, 20] });
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const pendingPaymentsListParams = createApiParams(
    {
      businessAreaSlug: businessArea,
      programCode: programId,
      id,
    },
    listVariables,
  );
  const {
    data: householdsData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPendingPaymentList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsTargetPopulationsPendingPaymentsList,
      pendingPaymentsListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsPendingPaymentsList(
        pendingPaymentsListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('People')}
        headCells={headCells}
        isLoading={isLoading}
        isFetching={isFetching}
        error={error}
        tableState={table}
        data={householdsData}
        renderRow={(row: PendingPayment) => (
          <TargetPopulationPeopleTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
