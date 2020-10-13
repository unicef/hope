import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { choicesToDict, formatCurrency } from '../../../utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../../__generated__/graphql';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { UniversalMoment } from '../../UniversalMoment';

interface LookUpHouseholdTableRowProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}

export function LookUpHouseholdTableRow({
  household,
  choicesData,
}: LookUpHouseholdTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const residenceStatusChoiceDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.unicefId}
    >
      <TableCell align='left'>{household.unicefId}</TableCell>
      <TableCell align='left'>{household.headOfHousehold.fullName}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.adminArea?.title || '-'}</TableCell>
      <TableCell align='left'>
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(household.totalCashReceived)}
      </TableCell>
      <TableCell align='right'>
        <UniversalMoment>{household.firstRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
