import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';

interface PaymentVerificationTableProps {
  filter?;
  businessArea: string;
  canViewDetails: boolean;
}
function PaymentVerificationTable({
  filter,
  canViewDetails,
  businessArea,
}: PaymentVerificationTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const filterVariables = useMemo(
    () => ({
      programCode: programId,
      businessAreaSlug: businessArea,
      search: filter.search,
      paymentVerificationSummaryStatus: filter.paymentVerificationSummaryStatus,
      fsp: filter.serviceProvider,
      deliveryMechanism: filter.deliveryTypes,
      startDate: filter.startDate,
      endDate: filter.endDate,
      isPaymentPlan: true,
    }),
    [
      programId,
      businessArea,
      filter.search,
      filter.paymentVerificationSummaryStatus,
      filter.serviceProvider,
      filter.deliveryTypes,
      filter.startDate,
      filter.endDate,
    ],
  );

  const table = useTableState({ resetPageOn: filterVariables });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );
  const paymentVerificationsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );
  const { data: countData } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentVerificationsCountRetrieve,
      paymentVerificationsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsCountRetrieve(
        paymentVerificationsCountParams,
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });
  const paymentVerificationsListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    listVariables,
  );
  const {
    data: paymentPlansData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPaymentVerificationPlanListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentVerificationsList,
      paymentVerificationsListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsList(
        paymentVerificationsListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  const itemsCount = usePersistedCount(page, countData);

  return (
    <UniversalRestTable
      title={t('List of Payment Plans')}
      headCells={headCells}
      data={paymentPlansData}
      isLoading={isLoading}
      isFetching={isFetching}
      error={error}
      tableState={table}
      itemsCount={itemsCount}
      renderRow={(paymentPlan) => (
        <PaymentVerificationTableRow
          key={paymentPlan.id}
          plan={paymentPlan}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
}

export default withErrorBoundary(
  PaymentVerificationTable,
  'PaymentVerificationTable',
);
