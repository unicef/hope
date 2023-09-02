import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { programCycleStatusToColor } from '../../../utils/utils';
import { BlackLink } from '../../core/BlackLink';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';
import { EditProgramCycle } from '../../../containers/dialogs/programs/programCycles/EditProgramCycle';
import { RemoveProgramCycle } from '../../../containers/dialogs/programs/programCycles/RemoveProgramCycle';

interface ProgramCyclesTableRowProps {
  canViewProgramCycleDetails: boolean;
  canEditProgramCycle: boolean;
  canRemoveProgramCycle: boolean;
  row;
  statusChoices: { [id: number]: string };
}

export const ProgramCyclesTableRow = ({
  canViewProgramCycleDetails,
  canEditProgramCycle,
  canRemoveProgramCycle,
  row,
  statusChoices,
}: ProgramCyclesTableRowProps): React.ReactElement => {
  const detailsPath = '';
  const handleRowClick = (): void => {
    //eslint-disable-next-line no-console
    console.log('handleRowClick');
  };
  return (
    <ClickableTableRow onClick={handleRowClick} hover role='checkbox' key={0}>
      <TableCell align='left'>
        {canViewProgramCycleDetails ? (
          <BlackLink to={detailsPath}>P-84273</BlackLink>
        ) : (
          'P-84273'
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={statusChoices[row.status]}
          statusToColor={programCycleStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='right'>-</TableCell>
      <TableCell align='right'>-</TableCell>
      <TableCell align='right'>-</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>
        <UniversalMoment>date</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <EditProgramCycle
          program={row}
          canEditProgramCycle={canEditProgramCycle}
        />
      </TableCell>
      <TableCell align='left'>
        <RemoveProgramCycle
          program={row}
          canRemoveProgramCycle={canRemoveProgramCycle}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
