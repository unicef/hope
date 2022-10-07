import { TableRow } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { AnonTableCell } from '../../../../components/core/Table/AnonTableCell';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  householdStatusToColor,
  verificationRecordsStatusToColor,
} from '../../../../utils/utils';
import { PaymentVerificationNode } from '../../../../__generated__/graphql';

interface VerificationRecordsTableRowProps {
  paymentVerification: PaymentVerificationNode;
  canViewRecordDetails: boolean;
  // selected: Array<string>;
  // checkboxClickHandler: () => void;
}

export function VerificationRecordsTableRow({
  paymentVerification,
  canViewRecordDetails,
}: VerificationRecordsTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();

  return (
    <TableRow hover role='checkbox' key={paymentVerification.id}>
      <TableCell align='left'>
        {canViewRecordDetails ? (
          <BlackLink to={`/${businessArea}/verification-records/${paymentVerification.id}`}>
            {paymentVerification.paymentRecord?.caId}
          </BlackLink>
        ) : (
          <span>{paymentVerification.paymentRecord?.caId}</span>
        )}
      </TableCell>
      <TableCell align='left'>
        {paymentVerification.paymentVerificationPlan.verificationChannel}
      </TableCell>
      <TableCell align='left'>
        {paymentVerification.paymentVerificationPlan.unicefId}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={paymentVerification.status}
          statusToColor={verificationRecordsStatusToColor}
        />
      </TableCell>
      <AnonTableCell>
        {paymentVerification.paymentRecord.household.headOfHousehold.fullName}
      </AnonTableCell>
      <TableCell align='left'>
        {paymentVerification.paymentRecord.household.unicefId}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={paymentVerification.paymentRecord.household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentVerification.paymentRecord.deliveredQuantity,
          paymentVerification.paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentVerification.receivedAmount,
          paymentVerification.paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='left'>
        {paymentVerification.paymentRecord.household.headOfHousehold.phoneNo}
      </TableCell>
      <TableCell align='left'>
        {paymentVerification.paymentRecord.household.headOfHousehold.phoneNoAlternative ||
          '-'}
      </TableCell>
    </TableRow>
  );
}
