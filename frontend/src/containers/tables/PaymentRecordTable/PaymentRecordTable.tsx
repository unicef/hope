import React, { ReactElement } from 'react';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './PaymentRecordTableHeadCells';
import { PaymentRecordTableRow } from './PaymentRecordTableRow';

interface PaymentRecordTableProps {
  cashPlan: CashPlanNode;
}
export function PaymentRecordTable({
  cashPlan,
}: PaymentRecordTableProps): ReactElement {
  const initialVariables = {
    cashPlan: cashPlan.id,
  };
  return (
    <UniversalTable<PaymentRecordNode, AllPaymentRecordsQueryVariables>
      title='Payment Records'
      headCells={headCells}
      query={useAllPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
      initialVariables={initialVariables}
      renderRow={(row) => <PaymentRecordTableRow paymentRecord={row} />}
    />
  );
}
