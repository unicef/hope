import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import Moment from 'react-moment';
import React from 'react';
import { useHistory } from 'react-router-dom';
import {
  CashPlanNode,
  HouseholdNode,
  IndividualNode,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import {
  cashPlanStatusToColor,
  decodeIdString,
  formatCurrency,
  getAgeFromDob,
  sexToCapitalize,
} from '../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface IndividualsListTableRowProps {
  individual: IndividualNode;
}

export function IndividualsListTableRow({
  individual,
}: IndividualsListTableRowProps) {
  const history = useHistory();
  const businessArea = useBusinessArea();
  let age: number | string = 'N/A';
  if (individual.dob) {
    age = getAgeFromDob(individual.dob);
  }
  const handleClick = (): void => {
    const path = `/${businessArea}/population/individuals/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={individual.id}
    >
      <TableCell align='left'>{decodeIdString(individual.id)}</TableCell>
      <TableCell align='left'>{individual.fullName}</TableCell>
      <TableCell align='left'>
        {decodeIdString(individual.household.id)}
      </TableCell>
      <TableCell align='right'>{age}</TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align='left'>{individual.household.location.title}</TableCell>
    </ClickableTableRow>
  );
}
