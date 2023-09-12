import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../../components/core/BlackLink';
import { StatusBox } from '../../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../../components/core/UniversalMoment';
import { programCycleStatusToColor } from '../../../../../utils/utils';
import { useBaseUrl } from '../../../../../hooks/useBaseUrl';

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
  const { baseUrl } = useBaseUrl();
  const history = useHistory();
  const {
    id,
    unicefId,
    name,
    status,
    totalEntitledQuantity,
    startDate,
    endDate,
  } = programCycle;

  const detailsPath = `/${baseUrl}/payment-module/program-cycles/${id}/`;
  const handleRowClick = (): void => {
    if (canViewProgramCycleDetails) {
      history.push(detailsPath);
    }
    return null;
  };

  return (
    <ClickableTableRow onClick={handleRowClick} hover role='checkbox'>
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
      <TableCell align='left'>
        <UniversalMoment>{startDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{endDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
