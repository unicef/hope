import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { HouseholdNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../core/Table/ClickableTableRow';
import { AnonTableCell } from '../../../core/Table/AnonTableCell';
import { BlackLink } from '../../../core/BlackLink';

interface EnrollmentHouseholdTableRowProps {
  household: HouseholdNode;
  canViewDetails?: boolean;
}

export function EnrollmentHouseholdTableRow({
  household,
  canViewDetails,
}): React.ReactElement<EnrollmentHouseholdTableRowProps> {
  const businessArea = useBusinessArea();
  const householdDetailsPath = `/${businessArea}/population/household/${household.id}`;
  const handleClick = (): void => {
    const win = window.open(householdDetailsPath, '_blank');
    if (win != null) {
      win.focus();
    }
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
        ) : (
          household.unicefId
        )}
      </TableCell>
      <AnonTableCell>{household.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.adminArea?.name || '-'}</TableCell>
      <TableCell align='left'>
        {household.selection?.vulnerabilityScore == null
          ? '-'
          : household.selection?.vulnerabilityScore}
      </TableCell>
    </ClickableTableRow>
  );
}
