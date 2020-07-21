import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { PaymentVerificationNodeEdge } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import {
  decodeIdString,
  formatCurrency,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface VerificationRecordsTableRowProps {
  record: PaymentVerificationNodeEdge;
}

export function VerificationRecordsTableRow({ record }) {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/verification-records/${record.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={record.id}
    >
      <TableCell align='left'>{decodeIdString(record.id)}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={record.status}
            statusToColor={verificationRecordsStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.headOfHousehold.fullName}
      </TableCell>
      <TableCell align='left'>
        {decodeIdString(record.paymentRecord.household.id)}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(record.paymentRecord.deliveredQuantity)}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(record.receivedAmount)}
      </TableCell>
    </ClickableTableRow>
  );
}
