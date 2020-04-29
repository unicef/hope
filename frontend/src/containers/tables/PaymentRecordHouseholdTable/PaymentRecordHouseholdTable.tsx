import React, { ReactElement } from 'react';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  HouseholdNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './PaymentRecordHouseholdTableHeadCells';
import { PaymentRecordHouseholdTableRow } from './PaymentRecordHouseholdTableRow';

interface PaymentRecordTableProps {
  cashPlan?: CashPlanNode;
  household?: HouseholdNode;
  openInNewTab?: boolean;
}
export function PaymentRecordHouseholdTable({
  household,
  openInNewTab = false,
}: PaymentRecordTableProps): ReactElement {
  const initialVariables = {
    household: household && household.id,
  };
  return (
    <UniversalTable<PaymentRecordNode, AllPaymentRecordsQueryVariables>
      title='Payment Records'
      headCells={headCells}
      query={useAllPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordHouseholdTableRow
          paymentRecord={row}
          openInNewTab={openInNewTab}
        />
      )}
    />
  );
}
