import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentPlansQuery,
  AllPaymentPlansQueryVariables,
  useAllPaymentPlansQuery,
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
  const initialVariables: AllPaymentPlansQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
    totalEntitledQuantity: filter.totalEntitledQuantity,
    dispersionStartDate: filter.dispersionStartDate,
    dispersionEndDate: filter.dispersionEndDate,
  };

  return (
    <UniversalTable<
      AllPaymentPlansQuery['allPaymentPlans']['edges'][number]['node'],
      AllPaymentPlansQueryVariables
    >
      title={t('Payment Plans')}
      headCells={headCells}
      query={useAllPaymentPlansQuery}
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
