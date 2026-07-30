import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { usePersistedCount } from '@hooks/usePersistedCount';

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
  const [page, setPage] = useState(0);
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const initialQueryVariables = useMemo(
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

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);
  const paymentVerificationsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
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
    queryVariables,
    { withPagination: true },
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
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      page={page}
      setPage={setPage}
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
