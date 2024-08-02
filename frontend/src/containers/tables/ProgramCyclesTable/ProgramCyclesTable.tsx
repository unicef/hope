import React, { ReactElement, useEffect, useState } from 'react';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { StatusBox } from '@core/StatusBox';
import { programCycleStatusToColor } from '@utils/utils';
import { UniversalMoment } from '@core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/tables/ProgramCyclesTable/HeadCells';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import {
  fetchProgramCycles,
  ProgramCycle,
  ProgramCyclesQuery,
} from '@api/programCycleApi';
import { BlackLink } from '@core/BlackLink';

interface ProgramCyclesTableProps {
  program;
  filters;
}

export const ProgramCyclesTable = ({
  program,
  filters,
}: ProgramCyclesTableProps) => {
  const [queryVariables, setQueryVariables] = useState<ProgramCyclesQuery>({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
    ...filters,
  });

  const { businessArea } = useBaseUrl();

  const { data, refetch, error, isLoading } = useQuery({
    queryKey: ['programCycles', businessArea, program.id, queryVariables],
    queryFn: async () => {
      return fetchProgramCycles(businessArea, program.id, queryVariables);
    },
  });

  useEffect(() => {
    setQueryVariables((oldVariables) => ({ ...oldVariables, ...filters }));
  }, [filters]);

  useEffect(() => {
    void refetch();
  }, [queryVariables, refetch]);

  const renderRow = (row: ProgramCycle): ReactElement => (
    <ClickableTableRow key={row.id} data-cy="program-cycle-row">
      <TableCell data-cy={`program-cycle-id-${row.id}`}>
        <BlackLink to={`./${row.id}`}>{row.unicef_id}</BlackLink>
      </TableCell>
      <TableCell data-cy={`program-cycle-title-${row.id}`}>
        {row.title}
      </TableCell>
      <TableCell data-cy={`program-cycle-status-${row.id}`}>
        <StatusBox
          status={row.status}
          statusToColor={programCycleStatusToColor}
        />
      </TableCell>
      <TableCell data-cy={`program-cycle-total-entitled-quantity-${row.id}`}>
        {row.total_entitled_quantity_usd || '-'}
      </TableCell>
      <TableCell data-cy={`program-cycle-start-date-${row.id}`}>
        <UniversalMoment>{row.start_date}</UniversalMoment>
      </TableCell>
      <TableCell data-cy={`program-cycle-end-date-${row.id}`}>
        <UniversalMoment>{row.end_date}</UniversalMoment>
      </TableCell>
      <TableCell data-cy={`program-cycle-details-btn-${row.id}`}>
        {/*  TODO add actions finish, reactivate */}
      </TableCell>
    </ClickableTableRow>
  );

  return (
    <UniversalRestTable
      title="Program Cycles"
      renderRow={renderRow}
      headCells={headCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
