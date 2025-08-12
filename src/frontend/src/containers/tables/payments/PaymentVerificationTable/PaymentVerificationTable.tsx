import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';
import { CountResponse } from '@restgenerated/models/CountResponse';

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
  const initialQueryVariables = useMemo(
    () => ({
      programSlug: programId,
      businessAreaSlug: businessArea,
      search: filter.search,
      paymentVerificationSummaryStatus: filter.paymentVerificationSummaryStatus,
      fsp: filter.serviceProvider,
      deliveryMechanism: filter.deliveryTypes,
      startDate: filter.startDate,
      endDate: filter.endDate,
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
  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsHouseholdsCount',
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
  });
  const {
    data: paymentPlansData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentVerificationPlanListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansList',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  return (
    <UniversalRestTable
      title={t('List of Payment Plans')}
      headCells={headCells}
      data={paymentPlansData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      itemsCount={countData?.count}
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
