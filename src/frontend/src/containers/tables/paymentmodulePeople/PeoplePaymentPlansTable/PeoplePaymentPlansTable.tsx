import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  useAllPaymentPlansForTableQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { PeoplePaymentPlanTableRow } from './PeoplePaymentPlanTableRow';
import { headCells } from './PeoplePaymentPlansHeadCells';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface PeoplePaymentPlansTableProps {
  filter;
  canViewDetails: boolean;
}

export const PeoplePaymentPlansTable = ({
  filter,
  canViewDetails,
}: PeoplePaymentPlansTableProps): ReactElement => {
  const { t } = useTranslation();
  const { programId, businessArea } = useBaseUrl();
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom || null,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo || null,
    dispersionStartDate: filter.dispersionStartDate || null,
    dispersionEndDate: filter.dispersionEndDate || null,
    isFollowUp: filter.isFollowUp ? true : null,
    program: programId,
    isPaymentPlan: true,
  };

  return (
    <UniversalTable<PaymentPlanNode, AllPaymentPlansForTableQueryVariables>
      defaultOrderBy="-createdAt"
      title={t('Payment Plans')}
      headCells={headCells}
      query={useAllPaymentPlansForTableQuery}
      queriedObjectName="allPaymentPlans"
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PeoplePaymentPlanTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};

export default withErrorBoundary(
  PeoplePaymentPlansTable,
  'PeoplePaymentPlansTable',
);
