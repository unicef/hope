import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { ImportedHouseholdMinimalFragment } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { decodeIdString } from '../../../../utils/utils';
import { FlagTooltip } from '../../../../components/FlagTooltip';
import { UniversalMoment } from '../../../../components/UniversalMoment';
import { AnonTableCell } from '../../../../components/table/AnonTableCell';
import { BlackLink } from '../../../../components/BlackLink';

interface PaymentRecordTableRowProps {
  household: ImportedHouseholdMinimalFragment;
}

export function ImportedHouseholdTableRow({
  household,
}: PaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const householdPath = `/${businessArea}/registration-data-import/household/${household.id}`;
  const handleClick = (): void => {
    const win = window.open(householdPath, '_blank');
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
      <TableCell align='left'>
        {household.hasDuplicates && (
          <FlagTooltip message='Possible duplicates' />
        )}
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={householdPath}>{decodeIdString(household.id)}</BlackLink>
      </TableCell>
      <AnonTableCell>{household?.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align='right'>{household.size}</TableCell>
      <TableCell align='left'>{household.admin2Title}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{household.firstRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
