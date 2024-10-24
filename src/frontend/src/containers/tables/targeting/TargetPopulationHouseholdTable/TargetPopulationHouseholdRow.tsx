import * as React from 'react';
import TableCell from '@mui/material/TableCell';
import { HouseholdNode } from '@generated/graphql';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
  canViewDetails?: boolean;
}

export function TargetPopulationHouseholdTableRow({
  household,
  canViewDetails,
}): React.ReactElement<TargetPopulationHouseholdTableRowProps> {
  const { baseUrl } = useBaseUrl();
  const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;
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
      role="checkbox"
      data-cy="target-population-household-row"
      key={household.id}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
        ) : (
          household.unicefId
        )}
      </TableCell>
      <AnonTableCell>{household.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align="left">{household.size}</TableCell>
      <TableCell align="left">{household.adminArea?.name || '-'}</TableCell>
      <TableCell align="left">
        {household.selection?.vulnerabilityScore == null
          ? '-'
          : household.selection?.vulnerabilityScore}
      </TableCell>
    </ClickableTableRow>
  );
}
