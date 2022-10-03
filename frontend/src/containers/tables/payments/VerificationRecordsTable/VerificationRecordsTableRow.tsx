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
  record: PaymentVerificationNode;
  canViewRecordDetails: boolean;
  // selected: Array<string>;
  // checkboxClickHandler: () => void;
}

export function VerificationRecordsTableRow({
  record,
  canViewRecordDetails,
}: VerificationRecordsTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();

  return (
    <TableRow hover role='checkbox' key={record.id}>
      <TableCell align='left'>
        {canViewRecordDetails ? (
          <BlackLink to={`/${businessArea}/verification-records/${record.id}`}>
            {record.paymentRecord?.caId}
          </BlackLink>
        ) : (
          <span>{record.paymentRecord?.caId}</span>
        )}
      </TableCell>
      <TableCell align='left'>
        {record.paymentVerificationPlan.verificationChannel}
      </TableCell>
      <TableCell align='left'>
        {record.paymentVerificationPlan.unicefId}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={record.status}
          statusToColor={verificationRecordsStatusToColor}
        />
      </TableCell>
      <AnonTableCell>
        {record.paymentRecord.household.headOfHousehold.fullName}
      </AnonTableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.unicefId}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={record.paymentRecord.household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          record.paymentRecord.deliveredQuantity,
          record.paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          record.receivedAmount,
          record.paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.headOfHousehold.phoneNo}
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.headOfHousehold.phoneNoAlternative ||
          '-'}
      </TableCell>
    </TableRow>
  );
}
