import { fetchProgramCycles, ProgramCycle } from '@api/programCycleApi';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { DeleteProgramCycle } from '@containers/tables/ProgramCycle/DeleteProgramCycle';
import { EditProgramCycle } from '@containers/tables/ProgramCycle/EditProgramCycle';
import headCells from '@containers/tables/ProgramCycle/HeadCells';
import { AddNewProgramCycle } from '@containers/tables/ProgramCycle/NewProgramCycle/AddNewProgramCycle';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { ProgramQuery, ProgramStatus } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import TableCell from '@mui/material/TableCell';
import { useQuery } from '@tanstack/react-query';
import { programCycleStatusToColor } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

interface ProgramCyclesTableProgramDetailsProps {
  program: ProgramQuery['program'];
}

export const ProgramCyclesTableProgramDetails = ({
  program,
}: ProgramCyclesTableProgramDetailsProps) => {
  const [queryVariables, setQueryVariables] = useState({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
  });
  const { businessArea, baseUrl, programId } = useBaseUrl();
  const permissions = usePermissions();
  const canCreateProgramCycle =
    program.status === ProgramStatus.Active &&
    hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_CREATE, permissions);

  const { data, error, isLoading } = useQuery({
    queryKey: ['programCycles', businessArea, program.id, queryVariables],
    queryFn: async () => {
      return fetchProgramCycles(businessArea, program.id, queryVariables);
    },
  });

  const canViewDetails = programId !== 'all';

  const renderRow = (row: ProgramCycle): ReactElement => {
    const detailsUrl = `/${baseUrl}/payment-module/program-cycles/${row.id}`;

    const canEditProgramCycle =
      (row.status === 'Draft' || row.status === 'Active') &&
      hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE, permissions);

    const hasPermissionToDelete = hasPermissions(
      PERMISSIONS.PM_PROGRAMME_CYCLE_DELETE,
      permissions,
    );
    return (
      <ClickableTableRow key={row.id} data-cy="program-cycle-row">
        <TableCell data-cy="program-cycle-title">
          {canViewDetails ? (
            <BlackLink to={detailsUrl}>{row.title}</BlackLink>
          ) : (
            row.title
          )}
        </TableCell>
        <TableCell data-cy="program-cycle-status">
          <StatusBox
            status={row.status}
            statusToColor={programCycleStatusToColor}
          />
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-entitled-quantity"
        >
          {row.total_entitled_quantity_usd || '-'}
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-undelivered-quantity"
        >
          {row.total_undelivered_quantity_usd || '-'}
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-delivered-quantity"
        >
          {row.total_delivered_quantity_usd || '-'}
        </TableCell>
        <TableCell data-cy="program-cycle-start-date">
          <UniversalMoment>{row.start_date}</UniversalMoment>
        </TableCell>
        <TableCell data-cy="program-cycle-end-date">
          <UniversalMoment>{row.end_date}</UniversalMoment>
        </TableCell>

        <TableCell data-cy="program-cycle-details-btn">
          {program.status === 'ACTIVE' && (
            <>
              {canEditProgramCycle && (
                <EditProgramCycle program={program} programCycle={row} />
              )}

              {row.can_remove_cycle && hasPermissionToDelete && (
                <DeleteProgramCycle program={program} programCycle={row} />
              )}
            </>
          )}
        </TableCell>
      </ClickableTableRow>
    );
  };

  if (isLoading) {
    return null;
  }

  const actions = [];

  if (canCreateProgramCycle) {
    actions.push(
      <AddNewProgramCycle
        key="add-new"
        program={program}
        lastProgramCycle={data.results[data.results.length - 1]}
      />,
    );
  }

  return (
    <UniversalRestTable
      title="Programme Cycles"
      renderRow={renderRow}
      headCells={headCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      actions={actions}
    />
  );
};
