import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { DeleteProgramCycle } from '../../../containers/dialogs/programs/programCycles/DeleteProgramCycle';
import { EditProgramCycle } from '../../../containers/dialogs/programs/programCycles/EditProgramCycle';
import { programCycleStatusToColor } from '../../../utils/utils';
import { BlackLink } from '../../core/BlackLink';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';

interface ProgramCyclesTableRowProps {
  canViewProgramCycleDetails: boolean;
  canEditProgramCycle: boolean;
  canDeleteProgramCycle: boolean;
  programCycle;
  statusChoices: { [id: number]: string };
}

export const ProgramCyclesTableRow = ({
  canViewProgramCycleDetails,
  canEditProgramCycle,
  canDeleteProgramCycle,
  programCycle,
  statusChoices,
}: ProgramCyclesTableRowProps): React.ReactElement => {
  const {
    id,
    name,
    status,
    totalEntitledQuantity,
    totalUndeliveredQuantity,
    totalDeliveredQuantity,
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
    <ClickableTableRow onClick={handleRowClick} hover role='checkbox' key={0}>
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
      <TableCell align='right'>{totalUndeliveredQuantity || '-'}</TableCell>
      <TableCell align='right'>{totalDeliveredQuantity}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{startDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{endDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <EditProgramCycle
          programCycle={programCycle}
          canEditProgramCycle={canEditProgramCycle}
        />
      </TableCell>
      <TableCell align='left'>
        <DeleteProgramCycle
          programCycle={programCycle}
          canDeleteProgramCycle={canDeleteProgramCycle}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
