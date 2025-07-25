import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import DeleteProgramCycle from '@containers/tables/ProgramCycle/DeleteProgramCycle';
import EditProgramCycle from '@containers/tables/ProgramCycle/EditProgramCycle';
import headCells from '@containers/tables/ProgramCycle/HeadCells';
import AddNewProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/AddNewProgramCycle';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import TableCell from '@mui/material/TableCell';
import { useQuery } from '@tanstack/react-query';
import { programCycleStatusToColor } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { Status791Enum } from '@restgenerated/models/Status791Enum';
import { RestService } from '@restgenerated/services/RestService';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';

interface ProgramCyclesTableProgramDetailsProps {
  program: ProgramDetail;
}

const ProgramCyclesTableProgramDetails = ({
  program,
}: ProgramCyclesTableProgramDetailsProps) => {
  const [queryVariables, setQueryVariables] = useState({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
  });
  const { businessAreaSlug, baseUrl, programSlug } = useBaseUrl();
  const permissions = usePermissions();
  const canCreateProgramCycle =
    program.status === Status791Enum.ACTIVE &&
    hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_CREATE, permissions);

  const { data, error, isLoading } = useQuery({
    queryKey: ['programCycles', businessAreaSlug, program.slug, queryVariables],
    queryFn: async () => {
      return RestService.restBusinessAreasProgramsCyclesList({
        businessAreaSlug,
        programSlug: program.slug,
      });
    },
  });

  const canViewDetails = programSlug !== 'all';

  const renderRow = (row: ProgramCycleList): ReactElement => {
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
          data-cy="program-cycle-total-entitled-quantity-usd"
        >
          {row.totalEntitledQuantityUsd || '-'}
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-undelivered-quantity-usd"
        >
          {row.totalUndeliveredQuantityUsd || '-'}
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-delivered-quantity-usd"
        >
          {row.totalDeliveredQuantityUsd || '-'}
        </TableCell>
        <TableCell data-cy="program-cycle-start-date">
          <UniversalMoment>{row.startDate}</UniversalMoment>
        </TableCell>
        <TableCell data-cy="program-cycle-end-date">
          <UniversalMoment>{row.endDate}</UniversalMoment>
        </TableCell>

        <TableCell data-cy="program-cycle-details-btn">
          {program.status === 'ACTIVE' && (
            <>
              {canEditProgramCycle && (
                <EditProgramCycle program={program} programCycle={row} />
              )}

              {row.canRemoveCycle && hasPermissionToDelete && (
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
        lastProgramCycle={
          (data?.results || [])[(data?.results || []).length - 1]
        }
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

export default withErrorBoundary(
  ProgramCyclesTableProgramDetails,
  'ProgramCyclesTableProgramDetails',
);
