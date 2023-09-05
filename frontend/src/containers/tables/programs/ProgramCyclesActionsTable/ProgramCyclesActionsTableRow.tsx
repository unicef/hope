import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { DeleteProgramCycle } from '../../../dialogs/programs/programCycles/DeleteProgramCycle';
import { EditProgramCycle } from '../../../dialogs/programs/programCycles/EditProgramCycle';
import { programCycleStatusToColor } from '../../../../utils/utils';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';

interface ProgramCyclesActionsTableRowProps {
  canViewProgramCycleDetails: boolean;
  canEditProgramCycle: boolean;
  canDeleteProgramCycle: boolean;
  programCycle;
  statusChoices: { [id: number]: string };
}

export const ProgramCyclesActionsTableRow = ({
  canViewProgramCycleDetails,
  canEditProgramCycle,
  canDeleteProgramCycle,
  programCycle,
  statusChoices,
}: ProgramCyclesActionsTableRowProps): React.ReactElement => {
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
