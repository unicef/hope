import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BlackLink } from '../../../../components/core/BlackLink';
import { AnonTableCell } from '../../../../components/core/Table/AnonTableCell';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { WarningTooltip } from '../../../../components/core/WarningTooltip';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';

interface ImportedHouseholdTableRowProps {
  isMerged?: boolean,
  household;
}

export function ImportedHouseholdTableRow({
  isMerged,
  household,
}: ImportedHouseholdTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();

  const importedHouseholdPath = `/${businessArea}/registration-data-import/household/${household.id}`;
  const mergedHouseholdPath = `/${businessArea}/population/household/${household.id}`;
  const url = isMerged ? mergedHouseholdPath : importedHouseholdPath

  const handleClick = (): void => {
    const win = window.open(url, '_blank');
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
      data-cy='imported-households-row'
    >
      <TableCell align='left'>
        {household.hasDuplicates && (
          <WarningTooltip confirmed message={t('Household has Duplicates')} />
        )}
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={url}>{isMerged ? household.unicefId : household.importId}</BlackLink>
      </TableCell>
      <AnonTableCell>{household?.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align='right'>{household.size}</TableCell>
      <TableCell align='left'>{isMerged ? household.admin2?.name : household.admin2Title}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{household.firstRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
