import * as React from 'react';
import TableCell from '@mui/material/TableCell';
import { HouseholdNode } from '@generated/graphql';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface TargetPopulationPeopleTableRowProps {
  household: HouseholdNode;
  canViewDetails?: boolean;
}

export function TargetPopulationPeopleTableRow({
  household,
  canViewDetails,
}): React.ReactElement<TargetPopulationPeopleTableRowProps> {
  const { baseUrl } = useBaseUrl();
  const householdDetailsPath = `/${baseUrl}/population/people/${household.headOfHousehold.id}`;
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
      key={household.id}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>{household.headOfHousehold.unicefId}</BlackLink>
        ) : (
          household.unicefId
        )}
      </TableCell>
      <AnonTableCell>{household.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align="left">{household.adminArea?.name || '-'}</TableCell>
      <TableCell align="left">
        {household.selection?.vulnerabilityScore == null
          ? '-'
          : household.selection?.vulnerabilityScore}
      </TableCell>
    </ClickableTableRow>
  );
}
