import React, { ReactElement } from 'react';
import {
  useAllPaymentVerificationsQuery,
  PaymentVerificationNodeEdge,
  AllPaymentVerificationsQueryVariables,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';

// interface VerificationRecordsTableProps {
//   filter;
// }
export function VerificationRecordsTable({ id }): ReactElement {
  const initialVariables: AllPaymentVerificationsQueryVariables = {
    cashPlanPaymentVerification: id,
  };
  return (
    <UniversalTable<
      PaymentVerificationNodeEdge,
      AllPaymentVerificationsQueryVariables
    >
      title='Verification Records'
      headCells={headCells}
      query={useAllPaymentVerificationsQuery}
      queriedObjectName='allPaymentVerifications'
      initialVariables={initialVariables}
      renderRow={(row) => <VerificationRecordsTableRow record={row} />}
    />
  );
}
