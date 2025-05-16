import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { useQuery } from '@tanstack/react-query';
import { dateToIsoString } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';

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
  const initialQueryVariables = {
    programSlug: programId,
    businessAreaSlug: businessArea,
    search: filter.search,
    verificationStatus: filter.verificationStatus,
    serviceProvider: filter.serviceProvider,
    deliveryTypes: filter.deliveryTypes,
    startDate: dateToIsoString(filter.startDate, 'startOfDay'),
    endDate: dateToIsoString(filter.endDate, 'endOfDay'),
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

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
