import TableCell from '@mui/material/TableCell';
import { PaymentNode } from '@generated/graphql';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

interface TargetPopulationHouseholdTableRowProps {
  payment: PaymentNode;
  canViewDetails?: boolean;
}

export function TargetPopulationHouseholdTableRow({
  payment,
  canViewDetails,
}): ReactElement<TargetPopulationHouseholdTableRowProps> {
  const { baseUrl } = useBaseUrl();
  const householdDetailsPath = `/${baseUrl}/population/household/${payment.household.id}`;
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
      key={payment.household.id}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>
            {payment.household.unicefId}
          </BlackLink>
        ) : (
          payment.household.unicefId
        )}
      </TableCell>
      <AnonTableCell>
        {payment.household.headOfHousehold?.fullName}
      </AnonTableCell>
      <TableCell align="left">{payment.household.size}</TableCell>
      <TableCell align="left">
        {payment.household.admin2?.name || '-'}
      </TableCell>
      <TableCell align="left">
        {payment.vulnerabilityScore == null ? '-' : payment.vulnerabilityScore}
      </TableCell>
    </ClickableTableRow>
  );
}
