import { BlackLink } from '@components/core/BlackLink';
import { periodicDataUpdatesOnlineEditsStatusToColor } from 'src/utils/utils';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { TableCell } from '@mui/material';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUOnlineEditListList } from '@restgenerated/models/PaginatedPDUOnlineEditListList';

const onlineEditsHeadCells: HeadCell<any>[] = [
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'ID',
    dataCy: 'head-cell-id',
  },
  {
    id: 'name',
    numeric: false,
    disablePadding: false,
    label: 'Name',
    dataCy: 'head-cell-name',
  },
  {
    id: 'numberOfRecords',
    numeric: true,
    disablePadding: false,
    label: 'Number of Records',
    dataCy: 'head-cell-number-of-records',
  },
  {
    id: 'createdAt',
    numeric: false,
    disablePadding: false,
    label: 'Creation Date',
    dataCy: 'head-cell-creation-date',
  },
  {
    id: 'createdBy',
    numeric: false,
    disablePadding: false,
    label: 'Created by',
    dataCy: 'head-cell-created-by',
  },
  {
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
    dataCy: 'head-cell-status',
  },
  {
    id: 'empty',
    numeric: false,
    disablePadding: false,
    label: '',
    dataCy: 'head-cell-empty',
  },
];

const NewPeriodicDataUpdates = (): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();
  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug,
      programSlug: programId,
      ordering: 'created_at',
      status: ['NEW' as const],
    }),
    [businessAreaSlug, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery<PaginatedPDUOnlineEditListList>({
    queryKey: [
      'periodicDataUpdateOnlineEdits',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsList({
        businessAreaSlug,
        programSlug: programId,
        ordering: queryVariables.ordering,
        status: queryVariables.status,
      }),
    enabled: !!queryVariables.businessAreaSlug && !!queryVariables.programSlug,
  });

  const renderRow = (row: any): ReactElement => (
    <ClickableTableRow key={row.id} data-cy={`online-edit-row-${row.id}`}>
      <TableCell>
        <BlackLink
          to={`/${baseUrl}/population/individuals/online-templates/${row.id}`}
        >
          {row.id}
        </BlackLink>
      </TableCell>
      <TableCell>{row.name}</TableCell>
      <TableCell>{row.numberOfRecords}</TableCell>
      <TableCell>
        <UniversalMoment>{row.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell>{row.createdBy}</TableCell>
      <TableCell>
        <StatusBox
          status={row.status}
          statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
        />
      </TableCell>
      <TableCell />
    </ClickableTableRow>
  );

  return (
    <UniversalRestTable
      isOnPaper={true}
      renderRow={renderRow}
      headCells={onlineEditsHeadCells}
      data={data ?? []}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      title="New Periodic Data Updates"
      hidePagination={true}
    />
  );
};

export default NewPeriodicDataUpdates;
