import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import Moment from 'react-moment';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import { cashPlanStatusToColor } from '../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface CashPlanTableRowProps {
  cashPlan: CashPlanNode;
}

export function CashPlanTableRow({ cashPlan }: CashPlanTableRowProps) {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/cashplans/${cashPlan.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={cashPlan.id}
    >
      <TableCell align='left'>
        <div
          style={{
            textOverflow: 'ellipsis',
          }}
        >
          {cashPlan.cashAssistId}
        </div>
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={cashPlan.status}
            statusToColor={cashPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='right'>{cashPlan.numberOfHouseholds}</TableCell>
      <TableCell align='left'>{cashPlan.currency}</TableCell>
      <TableCell align='right'>
        {cashPlan.totalEntitledQuantity.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </TableCell>
      <TableCell align='right'>
        {cashPlan.totalDeliveredQuantity.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </TableCell>
      <TableCell align='right'>
        {cashPlan.totalUndeliveredQuantity.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </TableCell>
      <TableCell align='left'>
        <Moment format='MM/DD/YYYY'>{cashPlan.dispersionDate}</Moment>
      </TableCell>
    </ClickableTableRow>
  );
}
