import TableCell from '@mui/material/TableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { PendingPayment } from '@restgenerated/models/PendingPayment';

interface TargetPopulationHouseholdTableRowProps {
  payment: PendingPayment;
  canViewDetails?: boolean;
}

export function TargetPopulationHouseholdTableRow({
  payment,
  canViewDetails,
}:TargetPopulationHouseholdTableRowProps): ReactElement<TargetPopulationHouseholdTableRowProps> {
  const { baseUrl } = useBaseUrl();
  const householdDetailsPath = `/${baseUrl}/population/household/${payment.householdId}`;
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
      key={payment.id}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>
            {payment.householdUnicefId}
          </BlackLink>
        ) : (
          payment.householdUnicefId
        )}
      </TableCell>
      <AnonTableCell>
        {payment.hohFullName}
      </AnonTableCell>
      <TableCell align="left">{payment.householdSize}</TableCell>
      <TableCell align="left">
        {payment.householdAdmin2 || '-'}
      </TableCell>
      <TableCell align="left">
        {payment.vulnerabilityScore == null ? '-' : payment.vulnerabilityScore}
      </TableCell>
    </ClickableTableRow>
  );
}
