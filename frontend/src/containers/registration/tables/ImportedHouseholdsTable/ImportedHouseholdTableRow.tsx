import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BlackLink } from '../../../../components/BlackLink';
import { WarningTooltip } from '../../../../components/WarningTooltip';
import { AnonTableCell } from '../../../../components/table/AnonTableCell';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/UniversalMoment';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../../utils/utils';
import { ImportedHouseholdMinimalFragment } from '../../../../__generated__/graphql';

interface PaymentRecordTableRowProps {
  household: ImportedHouseholdMinimalFragment;
}

export function ImportedHouseholdTableRow({
  household,
}: PaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
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
          <WarningTooltip confirmed message={t('Houesehold has Duplicates')} />
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
