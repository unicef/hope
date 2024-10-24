import { TableRow } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { AnonTableCell } from '@core/Table/AnonTableCell';
import {
  formatCurrencyWithSymbol,
  householdStatusToColor,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { PaymentVerificationNode } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface VerificationRecordsTableRowProps {
  paymentVerification: PaymentVerificationNode;
  canViewRecordDetails: boolean;
  showStatusColumn?: boolean;
}

export function PeopleVerificationRecordsTableRow({
  paymentVerification,
  canViewRecordDetails,
  showStatusColumn = true,
}: VerificationRecordsTableRowProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();

  const nodeType = atob(paymentVerification.payment.id).split(':')[0];
  const linkPath = `/${baseUrl}/verification/payment${
    nodeType === 'PaymentRecordNode' ? '-record' : ''
  }/${paymentVerification.payment.id}`;

  return (
    <TableRow hover role="checkbox" key={paymentVerification.id}>
      <TableCell align="left">
        {canViewRecordDetails ? (
          <BlackLink to={linkPath}>
            {paymentVerification.payment?.unicefId}
          </BlackLink>
        ) : (
          <span>{paymentVerification.payment?.unicefId}</span>
        )}
      </TableCell>
      <TableCell align="left">
        {paymentVerification.paymentVerificationPlan.verificationChannel}
      </TableCell>
      <TableCell align="left">
        {paymentVerification.paymentVerificationPlan.unicefId}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentVerification.status}
          statusToColor={verificationRecordsStatusToColor}
        />
      </TableCell>
      <AnonTableCell>
        {paymentVerification.payment.household.headOfHousehold.fullName}
      </AnonTableCell>
      <TableCell align="left">
        {paymentVerification.payment.household.headOfHousehold.unicefId}
      </TableCell>
      {showStatusColumn && (
        <TableCell align="left">
          <StatusBox
            status={paymentVerification.payment.household.status}
            statusToColor={householdStatusToColor}
          />
        </TableCell>
      )}
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          paymentVerification.payment.deliveredQuantity,
          paymentVerification.payment.currency,
        )}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          paymentVerification.receivedAmount,
          paymentVerification.payment.currency,
        )}
      </TableCell>
      <TableCell align="left">
        {paymentVerification.payment.household.headOfHousehold.phoneNo}
      </TableCell>
      <TableCell align="left">
        {paymentVerification.payment.household.headOfHousehold
          .phoneNoAlternative || '-'}
      </TableCell>
    </TableRow>
  );
}
