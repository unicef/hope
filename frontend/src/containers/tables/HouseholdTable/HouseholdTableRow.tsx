import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { choicesToDict, formatCurrency } from '../../../utils/utils';
import { Flag } from '../../../components/Flag';
import { UniversalMoment } from '../../../components/UniversalMoment';

interface HouseHoldTableRowProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}

export function HouseHoldTableRow({
  household,
  choicesData,
}: HouseHoldTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const residanceStatusChoiceDict = choicesToDict(
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
      <TableCell align='left'>
        {household.sanctionListPossibleMatch && <Flag />}
      </TableCell>
      <TableCell align='left'>{household.unicefId}</TableCell>
      <TableCell align='left'>{household.headOfHousehold.fullName}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.adminArea?.title || '-'}</TableCell>
      <TableCell align='left'>
        {residanceStatusChoiceDict[household.residenceStatus]}
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
