import React, { ReactElement } from 'react';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './RegistrationDataImportTableHeadCells';
import { RegistrationDataImportTableRow } from './RegistrationDataImportTableRow';

interface PaymentRecordTableProps {
  cashPlan: CashPlanNode;
}
export function RegistrationDataImportTable({
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
      renderRow={(row) => <RegistrationDataImportTableRow paymentRecord={row} />}
    />
  );
}
