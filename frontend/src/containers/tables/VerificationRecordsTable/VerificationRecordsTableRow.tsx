import { TableRow } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import styled from 'styled-components';
import { BlackLink } from '../../../components/BlackLink';
import { StatusBox } from '../../../components/StatusBox';
import { AnonTableCell } from '../../../components/table/AnonTableCell';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { PaymentVerificationNode } from '../../../__generated__/graphql';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
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
        <StatusContainer>
          <StatusBox
            status={record.status}
            statusToColor={verificationRecordsStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <AnonTableCell>
        {record.paymentRecord.household.headOfHousehold.fullName}
      </AnonTableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.unicefId}
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
