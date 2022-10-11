import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllCashPlansAndPaymentPlansQueryVariables,
  useAllCashPlansAndPaymentPlansQuery,
  CashPlanAndPaymentPlanNode,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';

interface PaymentVerificationTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}
export function PaymentVerificationTable({
  filter,
  canViewDetails,
  businessArea,
}: PaymentVerificationTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables: AllCashPlansAndPaymentPlansQueryVariables = {
    businessArea,
    program: filter.program,
    search: filter.search,
    serviceProvider: filter.serviceProvider,
    deliveryType: filter.deliveryType,
    verificationStatus: filter.verificationStatus,
    startDateGte: filter.startDate,
    endDateLte: filter.endDate,
  };
  return (
    <UniversalTable<
      CashPlanAndPaymentPlanNode,
      AllCashPlansAndPaymentPlansQueryVariables
    >
      title={t('List of Cash Plans')}
      headCells={headCells}
      query={useAllCashPlansAndPaymentPlansQuery}
      queriedObjectName='allCashPlansAndPaymentPlans'
      initialVariables={initialVariables}
      renderRow={(cashPlanAndPaymentPlanNode) => (
        <PaymentVerificationTableRow
          key={cashPlanAndPaymentPlanNode.id}
          plan={cashPlanAndPaymentPlanNode}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
}
