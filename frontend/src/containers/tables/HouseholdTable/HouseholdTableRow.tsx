import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import Moment from 'react-moment';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanNode, HouseholdNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import { cashPlanStatusToColor, formatCurrency } from '../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface HouseHoldTableRowProps {
  household: HouseholdNode;
}

export function HouseHoldTableRow({ household }: HouseHoldTableRowProps) {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{household.householdCaId}</TableCell>
      <TableCell align='left'>
        {household.paymentRecords.edges[0].node.headOfHousehold}
      </TableCell>
      <TableCell align='right'>{household.familySize}</TableCell>
      <TableCell align='left'>{household.location.title}</TableCell>
      <TableCell align='right'>{household.residenceStatus}</TableCell>
      <TableCell align='right'>
        {formatCurrency(
          household.paymentRecords.edges[0].node.cashPlan
            .totalDeliveredQuantity,
        )}
      </TableCell>
      <TableCell align='right'>
        <Moment format='MM/DD/YYYY'>{household.createdAt}</Moment>
      </TableCell>
    </ClickableTableRow>
  );
}
