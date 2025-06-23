import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { ReactElement, useState } from 'react';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { UniversalMoment } from '@core/UniversalMoment';
import { StatusBox } from '@core/StatusBox';
import { programCycleStatusToColor } from '@utils/utils';
import headCells from '@containers/tables/ProgramCycle/HeadCells';
import AddNewProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/AddNewProgramCycle';
import DeleteProgramCycle from '@containers/tables/ProgramCycle/DeleteProgramCycle';
import EditProgramCycle from '@containers/tables/ProgramCycle/EditProgramCycle';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedProgramCycleListList } from '@restgenerated/models/PaginatedProgramCycleListList';
import { BlackLink } from '@core/BlackLink';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { Status791Enum } from '@restgenerated/models/Status791Enum';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { RestService } from '@restgenerated/services/RestService';

interface ProgramCyclesTableProgramDetailsProps {
  program: ProgramDetail;
}

export const ProgramCyclesTableProgramDetails = ({
  program,
}: ProgramCyclesTableProgramDetailsProps) => {
  const { businessArea, baseUrl, programId } = useBaseUrl();
  const [queryVariables, setQueryVariables] = useState({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
    businessAreaSlug: businessArea,
    programSlug: programId,
  });
  const permissions = usePermissions();
  const canCreateProgramCycle =
    program.status === Status791Enum.ACTIVE &&
    hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_CREATE, permissions);

  const { data, error, isLoading } = useQuery<PaginatedProgramCycleListList>({
    queryKey: ['programCycles', businessArea, program.id, queryVariables],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsCyclesList({
        businessAreaSlug: businessArea,
        programSlug: program.id,
        limit: queryVariables.limit,
        offset: queryVariables.offset,
        ordering: queryVariables.ordering,
      });
    },
  });

  const { data: dataProgramCyclesCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsCyclesCountRetrieve',
      businessArea,
      program.id,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsCyclesCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: program.id,
      }),
  });

  const canViewDetails = programId !== 'all';

  const renderRow = (row: ProgramCycleList): ReactElement => {
    const detailsUrl = `/${baseUrl}/payment-module/program-cycles/${row.id}`;
    const canEditProgramCycle =
      (row.status === 'Draft' || row.status === 'Active') &&
      hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE, permissions);
    const canDeleteProgramCycle =
      row.status === 'Draft' &&
      data.results.length > 1 &&
      hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_DELETE, permissions);
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
          {row.totalEntitledQuantityUsd || '-'}
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-undelivered-quantity"
        >
          {row.totalUndeliveredQuantityUsd || '-'}
        </TableCell>
        <TableCell
          align="right"
          data-cy="program-cycle-total-delivered-quantity"
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

              {canDeleteProgramCycle && (
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
        lastProgramCycle={data?.results[data?.results?.length - 1]}
      />,
    );
  }

  return (
    <UniversalRestTable
      title="Programme Cycles"
      renderRow={renderRow}
      headCells={headCells}
      itemsCount={dataProgramCyclesCount?.count}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      actions={actions}
    />
  );
};
