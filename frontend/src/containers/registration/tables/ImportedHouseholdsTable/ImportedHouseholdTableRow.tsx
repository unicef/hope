import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import moment from 'moment';
import { ImportedHouseholdMinimalFragment } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { decodeIdString } from '../../../../utils/utils';
import { FlagTooltip } from '../../../../components/FlagTooltip';

interface PaymentRecordTableRowProps {
  household: ImportedHouseholdMinimalFragment;
}

export function ImportedHouseholdTableRow({
  household,
}: PaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/household/${household.id}`;
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
      <TableCell align='left'>
        {household.hasDuplicates && (
          <FlagTooltip message='Possible duplicates' />
        )}
      </TableCell>
      <TableCell align='left'>{decodeIdString(household.id)}</TableCell>
      <TableCell align='left'>{household?.headOfHousehold?.fullName}</TableCell>
      <TableCell align='right'>{household.size}</TableCell>
      <TableCell align='left'>{household.admin1}</TableCell>
      <TableCell align='left'>
        {moment(household.firstRegistrationDate).format('DD MMM YYYY')}
      </TableCell>
    </ClickableTableRow>
  );
}
