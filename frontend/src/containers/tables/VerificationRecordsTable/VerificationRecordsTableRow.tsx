import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import Moment from 'react-moment';
import { PaymentVerificationNodeEdge } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import {
  decodeIdString,
  formatCurrency,
  paymentVerificationStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';

const StatusContainer = styled.div`
  width: 120px;
`;
interface VerificationRecordsTableRowProps {
  plan: PaymentVerificationNodeEdge;
}

export function VerificationRecordsTableRow({ record }) {
  const history = useHistory();
  const businessArea = useBusinessArea();
  console.log('🐥', record);
  const handleClick = (): void => {
    const path = `/${businessArea}/payment-verification/${record.id}`;
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
      {/* <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={plan.verificationStatus}
            statusToColor={paymentVerificationStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{plan.assistanceThrough}</TableCell>
      <TableCell align='left'>{plan.deliveryType}</TableCell>
      <TableCell align='right'>
        {formatCurrency(plan.totalDeliveredQuantity)}
      </TableCell>
      <TableCell align='left'>
        <Moment format='DD/MM/YYYY'>{plan.startDate}</Moment>-
        <Moment format='DD/MM/YYYY'>{plan.endDate}</Moment>
      </TableCell>
      <TableCell align='left'>{plan.program.name}</TableCell> */}
    </ClickableTableRow>
  );
}
