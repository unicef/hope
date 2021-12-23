import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { HouseholdNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/Table/ClickableTableRow';
import { AnonTableCell } from '../../../components/Table/AnonTableCell';
import { BlackLink } from '../../../components/BlackLink';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
  canViewDetails?: boolean;
}

export function TargetPopulationHouseholdTableRow({
  household,
  canViewDetails,
}): React.ReactElement<TargetPopulationHouseholdTableRowProps> {
  const businessArea = useBusinessArea();
  const householdDetailsPath = `/${businessArea}/population/household/${household.id}`;
  const handleClick = (): void => {
    const win = window.open(householdDetailsPath, '_blank');
    if (win != null) {
      win.focus();
    }
  };

  const renderHoHName = (): string => {
    const {
      headOfHousehold: { givenName, familyName, fullName },
    } = household;
    if (givenName && familyName) {
      return `${givenName} ${familyName}`;
    }
    return fullName;
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
      <AnonTableCell>{renderHoHName()}</AnonTableCell>
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
