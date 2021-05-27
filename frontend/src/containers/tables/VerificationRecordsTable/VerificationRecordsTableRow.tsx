import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import {useHistory} from 'react-router-dom';
import styled from 'styled-components';
import {TableRow} from '@material-ui/core';
import {PaymentVerificationNode} from '../../../__generated__/graphql';
import {useBusinessArea} from '../../../hooks/useBusinessArea';
import {formatCurrencyWithSymbol, verificationRecordsStatusToColor,} from '../../../utils/utils';
import {StatusBox} from '../../../components/StatusBox';
import {AnonTableCell} from '../../../components/table/AnonTableCell';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
const Pointer = styled.span`
  cursor: pointer;
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
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/verification-records/${record.id}`;
    history.push(path);
  };

  return (
    <TableRow hover role='checkbox' key={record.id}>
      <TableCell
        onClick={canViewRecordDetails ? handleClick : undefined}
        align='left'
      >
        <Pointer>{record.paymentRecord?.caId}</Pointer>
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
