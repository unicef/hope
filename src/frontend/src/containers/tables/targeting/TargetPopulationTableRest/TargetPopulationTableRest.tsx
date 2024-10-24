import { fetchTargetPopulations } from '@api/targetPopulationApi';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { TargetPopulationQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import { useQuery } from '@tanstack/react-query';
import { targetPopulationStatusToColor } from '@utils/utils';
import { ReactElement, useState } from 'react';

interface TargetPopulationTableProps {
  program: TargetPopulationQuery['program'];
}

const headCells: HeadCell<TargetPopulation>[] = [
  {
    id: 'name',
    label: 'Name',
    dataCy: 'name',
    numeric: false,
    disablePadding: true,
  },
  {
    id: 'status',
    label: 'Status',
    dataCy: 'status',
    numeric: false,
    disablePadding: true,
  },
  {
    id: 'total_households_count',
    label: 'Num. of Households',
    dataCy: 'num-of-households',
    numeric: true,
    disablePadding: true,
    disableSort: true,
  },
  {
    id: 'created_at',
    label: 'Date Created',
    dataCy: 'date-created',
    numeric: false,
    disablePadding: true,
  },
  {
    id: 'updated_at',
    label: 'Last Edited',
    dataCy: 'last-edited',
    numeric: false,
    disablePadding: true,
  },
  {
    id: 'created_by',
    label: 'Created By',
    dataCy: 'created-by',
    numeric: false,
    disablePadding: true,
  },
];

interface TargetPopulation {
  id: string;
  name: string;
  status: string;
  numHouseholds: number | null;
  dateCreated: string;
  lastEdited: string;
  createdBy: string;
}

export const TargetPopulationTableRest = ({
  program,
}: TargetPopulationTableProps) => {
  const [queryVariables, setQueryVariables] = useState({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
  });
  const { businessArea, baseUrl, programId } = useBaseUrl();

  const { data, error, isLoading } = useQuery({
    queryKey: ['targetPopulations', businessArea, program.id, queryVariables],
    queryFn: async () => {
      return fetchTargetPopulations(businessArea, program.id, queryVariables);
    },
  });

  const canViewDetails = programId !== 'all';

  const renderRow = (row: TargetPopulation): ReactElement => {
    const detailsUrl = `/${baseUrl}/payment-module/target-populations/${row.id}`;

    return (
      <ClickableTableRow key={row.id} data-cy="target-population-row">
        <TableCell data-cy="target-population-name">
          {canViewDetails ? (
            <BlackLink to={detailsUrl}>{row.name}</BlackLink>
          ) : (
            row.name
          )}
        </TableCell>
        <TableCell data-cy="target-population-status">
          <StatusBox
            status={row.status}
            statusToColor={targetPopulationStatusToColor}
          />
        </TableCell>
        <TableCell align="right" data-cy="target-population-num-households">
          {row.numHouseholds || '-'}
        </TableCell>
        <TableCell data-cy="target-population-date-created">
          <UniversalMoment>{row.dateCreated}</UniversalMoment>
        </TableCell>
        <TableCell data-cy="target-population-last-edited">
          <UniversalMoment>{row.lastEdited}</UniversalMoment>
        </TableCell>
        <TableCell data-cy="target-population-created-by">
          {row.createdBy}
        </TableCell>
      </ClickableTableRow>
    );
  };

  if (isLoading) {
    return null;
  }

  const actions = [];

  return (
    <UniversalRestTable
      title="Target Populations"
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
