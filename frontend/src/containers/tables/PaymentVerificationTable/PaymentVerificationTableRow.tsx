import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import Moment from 'react-moment';
import { CashPlanNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import {
  decodeIdString,
  formatCurrency,
  paymentVerificationStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface PaymentVerificationTableRowProps {
  plan: CashPlanNode;
}

export function PaymentVerificationTableRow({
  plan,
}: PaymentVerificationTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/payment-verification/${plan.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={plan.id}
    >
      <TableCell align='left'>{decodeIdString(plan.id)}</TableCell>
      <TableCell align='left'>
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
      <TableCell align='left'>{plan.program.name}</TableCell>
    </ClickableTableRow>
  );
}
