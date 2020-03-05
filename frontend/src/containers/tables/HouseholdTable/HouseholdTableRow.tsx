import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import Moment from 'react-moment';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanNode, HouseholdNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import { cashPlanStatusToColor, decodeIdString, formatCurrency } from '../../../utils/utils';

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
      <TableCell align='left'>{decodeIdString(household.id)}</TableCell>
      <TableCell align='left'>
        {household.headOfHousehold.fullName}
      </TableCell>
      <TableCell align='left'>{household.familySize}</TableCell>
      <TableCell align='left'>{household.location.title}</TableCell>
      <TableCell align='left'>{household.residenceStatus}</TableCell>
      <TableCell align='right'>
        {formatCurrency(
          household.totalCashReceived
        )}
      </TableCell>
      <TableCell align='right'>
        <Moment format='MM/DD/YYYY'>{household.registrationDate}</Moment>
      </TableCell>
    </ClickableTableRow>
  );
}
