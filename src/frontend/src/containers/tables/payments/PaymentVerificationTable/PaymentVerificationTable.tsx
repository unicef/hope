import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentPlansForTableQueryVariables,
  useAllPaymentPlansForTableQuery,
  PaymentPlanNode,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { dateToIsoString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';
import withErrorBoundary from '@components/core/withErrorBoundary';

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
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    search: filter.search,
    verificationStatus: filter.verificationStatus,
    serviceProvider: filter.serviceProvider,
    deliveryTypes: filter.deliveryTypes,
    startDate: dateToIsoString(filter.startDate, 'startOfDay'),
    endDate: dateToIsoString(filter.endDate, 'endOfDay'),
    program: programId,
  };
  return (
    <UniversalTable<PaymentPlanNode, AllPaymentPlansForTableQueryVariables>
      title={t('List of Payment Plans')}
      headCells={headCells}
      query={useAllPaymentPlansForTableQuery}
      queriedObjectName="allPaymentPlans"
      initialVariables={initialVariables}
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
