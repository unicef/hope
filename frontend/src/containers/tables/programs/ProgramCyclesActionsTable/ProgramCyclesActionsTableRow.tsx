import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { programCycleStatusToColor } from '../../../../utils/utils';
import { DeleteProgramCycle } from '../../../dialogs/programs/programCycles/DeleteProgramCycle';
import { EditProgramCycle } from '../../../dialogs/programs/programCycles/EditProgramCycle';

interface ProgramCyclesActionsTableRowProps {
  canViewProgramCycleDetails: boolean;
  canEditProgramCycle: boolean;
  canDeleteProgramCycle: boolean;
  programCycle;
  statusChoices: { [id: number]: string };
  itemsCount: number;
}

export const ProgramCyclesActionsTableRow = ({
  canViewProgramCycleDetails,
  canEditProgramCycle,
  canDeleteProgramCycle,
  programCycle,
  statusChoices,
  itemsCount,
}: ProgramCyclesActionsTableRowProps): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const {
    id,
    unicefId,
    name,
    status,
    totalEntitledQuantity,
    totalUndeliveredQuantity,
    totalDeliveredQuantity,
    startDate,
    endDate,
  } = programCycle;

  const detailsPath = `/${baseUrl}/payment-module/program-cycles/${id}`;

  return (
    <ClickableTableRow>
      <TableCell align='left'>
        {canViewProgramCycleDetails ? (
          <BlackLink to={detailsPath}>{unicefId}</BlackLink>
        ) : (
          unicefId
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
          itemsCount={itemsCount}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
