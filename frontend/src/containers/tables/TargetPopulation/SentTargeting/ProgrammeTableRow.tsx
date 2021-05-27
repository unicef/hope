import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import {useHistory} from 'react-router-dom';
import {HouseholdNode} from '../../../../__generated__/graphql';
import {useBusinessArea} from '../../../../hooks/useBusinessArea';
import {ClickableTableRow} from '../../../../components/table/ClickableTableRow';
import {AnonTableCell} from "../../../../components/table/AnonTableCell";

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
  canViewDetails?: boolean;
}

export function ProgrammeTableRow({
  household,
  canViewDetails = true,
}): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{household.unicefId}</TableCell>
      <AnonTableCell align='left'>{`${household.headOfHousehold.givenName} ${household.headOfHousehold.familyName}`}</AnonTableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.adminArea?.title || '-'}</TableCell>
      <TableCell align='left'>
        {household.selection?.vulnerabilityScore ||
        household.selection?.vulnerabilityScore === 0
          ? household.selection?.vulnerabilityScore
          : '-'}
      </TableCell>
    </ClickableTableRow>
  );
}
