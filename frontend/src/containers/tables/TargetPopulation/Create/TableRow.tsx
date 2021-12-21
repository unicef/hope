import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { ClickableTableRow } from '../../../../components/Table/ClickableTableRow';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { renderIndividualName } from '../../../../utils/utils';
import { HouseholdNode } from '../../../../__generated__/graphql';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
}

export function TargetPopulationHouseholdTableRow({
  household,
}): React.ReactElement {
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    const win = window.open(path, '_blank');
    if (win != null) {
      win.focus();
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{household.unicefId}</TableCell>
      <TableCell align='left'>
        {renderIndividualName(household.headOfHousehold)}
      </TableCell>
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
