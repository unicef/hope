import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentRecordTableHeadCells';
import { PaymentRecordTableRow } from './PaymentRecordTableRow';

interface PaymentRecordTableProps {
  cashPlan: CashPlanNode;
  openInNewTab?: boolean;
}
export function PaymentRecordTable({
  cashPlan,
  openInNewTab = false,
}: PaymentRecordTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables: AllPaymentRecordsQueryVariables = {
    parent: cashPlan.id,
  };
  return (
    <UniversalTable<PaymentRecordNode, AllPaymentRecordsQueryVariables>
      title={t('Payment Records')}
      headCells={headCells}
      query={useAllPaymentRecordsQuery}
      queriedObjectName="allPaymentRecords"
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordTableRow
          key={row.id}
          paymentRecord={row}
          openInNewTab={openInNewTab}
        />
      )}
    />
  );
}
