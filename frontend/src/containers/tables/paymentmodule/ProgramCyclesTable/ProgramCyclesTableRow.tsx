import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { programCycleStatusToColor } from '../../../../utils/utils';

interface ProgramCyclesTableRowProps {
  canViewProgramCycleDetails: boolean;
  programCycle;
  statusChoices: { [id: number]: string };
}

export const ProgramCyclesTableRow = ({
  canViewProgramCycleDetails,
  programCycle,
  statusChoices,
}: ProgramCyclesTableRowProps): React.ReactElement => {
  const {
    id,
    name,
    status,
    totalEntitledQuantity,

    startDate,
    endDate,
  } = programCycle;

  //TODO: add detailsPath
  const detailsPath = '';
  const handleRowClick = (): void => {
    //eslint-disable-next-line no-console
    console.log('handleRowClick');
  };

  return (
    <ClickableTableRow onClick={handleRowClick} hover role='checkbox'>
      <TableCell align='left'>
        {canViewProgramCycleDetails ? (
          <BlackLink to={detailsPath}>{id}</BlackLink>
        ) : (
          id
        )}
      </TableCell>
      <TableCell align='left'>{name}</TableCell>
      <TableCell align='left'>
        <StatusBox
          status={statusChoices[status]}
          statusToColor={programCycleStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>{totalEntitledQuantity || '-'}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{startDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{endDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
