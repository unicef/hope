import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  PaymentPlanNode,
  AllPaymentPlansForTableQueryVariables,
  useAllPaymentPlansForTableQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentPlansHeadCells';
import { PaymentPlanTableRow } from './PaymentPlanTableRow';

interface PaymentPlansTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}

export function PaymentPlansTable({
  filter,
  canViewDetails,
  businessArea,
}: PaymentPlansTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
    dispersionStartDate: filter.dispersionStartDate,
    dispersionEndDate: filter.dispersionEndDate,
  };

  return (
    <UniversalTable<PaymentPlanNode, AllPaymentPlansForTableQueryVariables>
      defaultOrderBy='-createdAt'
      title={t('Payment Plans')}
      headCells={headCells}
      query={useAllPaymentPlansForTableQuery}
      queriedObjectName='allPaymentPlans'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentPlanTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
}
