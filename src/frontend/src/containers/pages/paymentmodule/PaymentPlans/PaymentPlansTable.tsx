import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlansHeadCells';
import { PaymentPlanTableRow } from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlanTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { createApiParams } from '@utils/apiUtils';
import { usePersistedCount } from '@hooks/usePersistedCount';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import type { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import type { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

interface PaymentPlansTableProps {
  filter?: { search?: string; cycle?: string; status?: string[] };
}

export const PaymentPlansTable = ({
  filter,
}: PaymentPlansTableProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const filterVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      search: filter?.search || undefined,
      cycle: filter?.cycle || undefined,
      status: filter?.status?.length
        ? (filter.status as PaymentPlanStatusEnum[])
        : undefined,
    }),
    [businessArea, programId, filter?.search, filter?.cycle, filter?.status],
  );
  const table = useTableState({ resetPageOn: filterVariables });
  const { page } = table;

  const paymentPlansListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    { ...filterVariables, ...table.paginationParams },
  );
  const { data, isLoading, error } = useQuery<PaginatedPaymentPlanListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansList,
      paymentPlansListParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansList(
        paymentPlansListParams,
      ),
    enabled: !!businessArea && !!programId,
  });

  const paymentPlansCountParams = filterVariables;
  const { data: dataCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve,
      paymentPlansCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve(
        paymentPlansCountParams,
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
      renderRow={(row: PaymentPlanList) => (
        <PaymentPlanTableRow key={row.id} paymentPlan={row} />
      )}
    />
  );
};
