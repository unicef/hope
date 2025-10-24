import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { AnonTableCell } from '@core/Table/AnonTableCell';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TableRow } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { PaymentList } from '@restgenerated/models/PaymentList';
import {
  formatCurrencyWithSymbol,
  householdStatusToColor,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';

interface VerificationRecordsTableRowProps {
  payment: PaymentList;
  canViewRecordDetails: boolean;
  showStatusColumn?: boolean;
}

export function PeopleVerificationRecordsTableRow({
  payment,
  canViewRecordDetails,
  showStatusColumn = true,
}: VerificationRecordsTableRowProps): ReactElement {
  const { baseUrl } = useBaseUrl();

  const linkPath = `/${baseUrl}/verification/payment/${payment.id}`;

  return (
    <TableRow hover role="checkbox" key={payment.id}>
      <TableCell align="left">
        {canViewRecordDetails ? (
          <BlackLink to={linkPath}>{payment?.unicefId}</BlackLink>
        ) : (
          <span>{payment?.unicefId}</span>
        )}
      </TableCell>
      <TableCell align="left">
        {payment.verification.verificationChannel}
      </TableCell>
      <TableCell align="left">
        {payment.verification.paymentVerificationPlanUnicefId}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={payment.status}
          statusToColor={verificationRecordsStatusToColor}
        />
      </TableCell>
      <AnonTableCell>{payment.hohFullName}</AnonTableCell>
      <TableCell align="left">{payment.householdUnicefId}</TableCell>
      {showStatusColumn && (
        <TableCell align="left">
          <StatusBox
            status={payment.householdStatus}
            statusToColor={householdStatusToColor}
          />
        </TableCell>
      )}
      <TableCell align="right">
        {formatCurrencyWithSymbol(payment.deliveredQuantity, payment.currency)}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          payment.verification.receivedAmount,
          payment.currency,
        )}
      </TableCell>
      <TableCell align="left">{payment.hohPhoneNo}</TableCell>
      <TableCell align="left">{payment.hohPhoneNoAlternative || '-'}</TableCell>
    </TableRow>
  );
}
