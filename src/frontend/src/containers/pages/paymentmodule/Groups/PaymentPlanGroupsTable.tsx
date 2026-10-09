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
import type { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

interface PaymentPlanGroupsTableProps {
  filter?: { search?: string; cycle?: string; status?: string[] };
}

export const PaymentPlanGroupsTable = ({
  filter,
}: PaymentPlanGroupsTableProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const filterVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      search: filter?.search || undefined,
      cycle: filter?.cycle || undefined,
      status: filter?.status?.length
        ? (filter.status as PaymentPlanGroupStatusEnum[])
        : undefined,
    }),
    [businessArea, programId, filter?.search, filter?.cycle, filter?.status],
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
      title={t('Payment Plans')}
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
