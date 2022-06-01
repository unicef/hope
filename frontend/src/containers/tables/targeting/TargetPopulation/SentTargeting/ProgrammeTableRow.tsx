import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../../components/core/BlackLink';
import { AnonTableCell } from '../../../../../components/core/Table/AnonTableCell';
import { ClickableTableRow } from '../../../../../components/core/Table/ClickableTableRow';
import { useBusinessArea } from '../../../../../hooks/useBusinessArea';
import { renderIndividualName } from '../../../../../utils/utils';

export function ProgrammeTableRow({
  household,
  canViewDetails = true,
}): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const householdDetailsPath = `/${businessArea}/population/household/${household.id}`;
  const handleClick = (): void => {
    history.push(householdDetailsPath);
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
      <AnonTableCell align='left'>
        {renderIndividualName(household.headOfHousehold)}
      </AnonTableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.adminArea?.name || '-'}</TableCell>
      <TableCell align='left'>
        {household.selection?.vulnerabilityScore ||
        household.selection?.vulnerabilityScore === 0
          ? household.selection?.vulnerabilityScore
          : '-'}
      </TableCell>
    </ClickableTableRow>
  );
}
