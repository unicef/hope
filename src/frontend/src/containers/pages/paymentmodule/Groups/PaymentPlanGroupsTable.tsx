import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsHeadCells';
import { PaymentPlanGroupTableRow } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { createApiParams } from '@utils/apiUtils';
import { usePersistedCount } from '@hooks/usePersistedCount';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedPaymentPlanGroupListList } from '@restgenerated/models/PaginatedPaymentPlanGroupListList';
import type { PaymentPlanGroupList } from '@restgenerated/models/PaymentPlanGroupList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useMemo } from 'react';

interface PaymentPlanGroupsTableProps {
  filter?: { search?: string; cycle?: string };
}

export const PaymentPlanGroupsTable = ({
  filter,
}: PaymentPlanGroupsTableProps): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const filterVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      search: filter?.search || undefined,
      cycle: filter?.cycle || undefined,
    }),
    [businessArea, programId, filter?.search, filter?.cycle],
  );
  const table = useTableState({ resetPageOn: filterVariables });
  const { page } = table;

  const groupsListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    { ...filterVariables, ...table.paginationParams },
  );
  const { data, isLoading, error } =
    useQuery<PaginatedPaymentPlanGroupListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
        groupsListParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlanGroupsList(
          groupsListParams,
        ),
      enabled: !!businessArea && !!programId,
    });

  const groupsCountParams = filterVariables;
  const { data: dataCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCountRetrieve,
      groupsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCountRetrieve(
        groupsCountParams,
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  const itemsCount = usePersistedCount(page, dataCount);

  return (
    <UniversalRestTable
      title="Groups"
      headCells={headCells}
      tableState={table}
      data={data}
      error={error}
      isLoading={isLoading}
      itemsCount={itemsCount}
      renderRow={(row: PaymentPlanGroupList) => (
        <PaymentPlanGroupTableRow key={row.id} group={row} />
      )}
    />
  );
};
