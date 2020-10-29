import React, { ReactElement } from 'react';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  LookUpPaymentRecordsQueryVariables,
  PaymentRecordNode,
  useLookUpPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpPaymentRecordTableHeadCells';
import { LookUpPaymentRecordTableRow } from './LookUpPaymentRecordTableRow';

interface LookUpPaymentRecordTableProps {
  cashPlanId: string;
  openInNewTab?: boolean;
}
export function LookUpPaymentRecordTable({
  cashPlanId,
  openInNewTab = false,
}: LookUpPaymentRecordTableProps): ReactElement {
  const initialVariables = {
    cashPlan: cashPlanId,
  };
  return (
    <UniversalTable<PaymentRecordNode, LookUpPaymentRecordsQueryVariables>
      headCells={headCells}
      query={useLookUpPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <LookUpPaymentRecordTableRow
          openInNewTab={openInNewTab}
          key={row.id}
          paymentRecord={row}
        />
      )}
    />
  );
}
