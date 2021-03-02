import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { choicesToDict, formatCurrencyWithSymbol } from '../../../utils/utils';
import { Flag } from '../../../components/Flag';
import { UniversalMoment } from '../../../components/UniversalMoment';
import { FlagTooltip } from '../../../components/FlagTooltip';
import { AnonTableCell } from '../../../components/table/AnonTableCell';

interface HouseHoldTableRowProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
  canViewDetails: boolean;
}

export function HouseHoldTableRow({
  household,
  choicesData,
  canViewDetails,
}: HouseHoldTableRowProps): React.ReactElement {
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
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={household.unicefId}
    >
      <TableCell align='left'>
        {household.hasDuplicates && <FlagTooltip />}
        {(household.sanctionListPossibleMatch ||
          household.sanctionListConfirmedMatch) && (
          <Flag confirmed={household.sanctionListConfirmedMatch} />
        )}
      </TableCell>
      <TableCell align='left'>{household.unicefId}</TableCell>
      <AnonTableCell>{household.headOfHousehold.fullName}</AnonTableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.admin2?.title || '-'}</TableCell>
      <TableCell align='left'>
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          household.totalCashReceived,
          household.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
