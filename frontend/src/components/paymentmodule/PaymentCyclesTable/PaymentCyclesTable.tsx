import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { headCells } from './PaymentCyclesHeadCells';
import { PaymentCyclesTableRow } from './PaymentCyclesTableRow';

interface PaymentCyclesTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}

export function PaymentCyclesTable({
  filter,
  canViewDetails,
  businessArea,
}: PaymentCyclesTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables: AllPaymentCyclesForTableQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
    startDate: filter.startDate,
    endDate: filter.endDate,
  };

  return (
    <UniversalTable<PaymentCycleNode, AllPaymentCyclesForTableQueryVariables>
      defaultOrderBy='-createdAt'
      title={t('Payment Cycles')}
      headCells={headCells}
      query={useAllPaymentCyclesForTableQuery}
      queriedObjectName='allPaymentCycles'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentCyclesTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
}
