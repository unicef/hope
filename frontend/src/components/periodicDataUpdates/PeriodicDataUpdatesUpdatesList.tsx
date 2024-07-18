import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { TableCell } from '@mui/material';
import { periodicDataUpdatesUpdatesStatusToColor } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { fetchPeriodicDataUpdateUpdates } from '@api/periodicDataUpdateApi';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface Update {
  id: string;
  template: string;
  created_at: string;
  created_by: string;
  status: string;
}

const updatesHeadCells: HeadCell<Update>[] = [
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'Import ID',
    dataCy: 'head-cell-import-id',
  },
  {
    id: 'template',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
    dataCy: 'head-cell-template-id',
  },
  {
    id: 'created_at',
    numeric: false,
    disablePadding: false,
    label: 'Import Date',
    dataCy: 'head-cell-import-date',
  },
  {
    id: 'created_by',
    numeric: false,
    disablePadding: false,
    label: 'Imported by',
    dataCy: 'head-cell-imported-by',
  },
  {
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
    dataCy: 'head-cell-status',
  },
];

const renderUpdateRow = (row: Update): ReactElement => (
  <ClickableTableRow key={row.id} data-cy={`update-row-${row.id}`}>
    <TableCell data-cy={`update-id-${row.id}`}>
      <BlackLink>{row.id}</BlackLink>
    </TableCell>
    <TableCell data-cy={`update-template-${row.id}`}>
      <BlackLink>{row.template}</BlackLink>
    </TableCell>
    <TableCell data-cy={`update-created-at-${row.id}`}>
      <UniversalMoment>{row.created_at}</UniversalMoment>
    </TableCell>
    <TableCell data-cy={`update-created-by-${row.id}`}>
      {row.created_by}
    </TableCell>
    <TableCell data-cy={`update-status-${row.id}`}>
      <StatusBox
        status={row.status}
        statusToColor={periodicDataUpdatesUpdatesStatusToColor}
      />
    </TableCell>
  </ClickableTableRow>
);

export const PeriodicDataUpdatesUpdatesList = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();

  const initialQueryVariables = {
    page: 1,
    page_size: 10,
    ordering: 'created_at',
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: updatesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: [
      'periodicDataUpdateUploads',
      businessAreaSlug,
      programId,
      queryVariables,
    ],
    queryFn: () =>
      fetchPeriodicDataUpdateUpdates(
        businessAreaSlug,
        programId,
        queryVariables,
      ),
  });

  return (
    <UniversalRestTable
      isOnPaper={false}
      renderRow={renderUpdateRow}
      headCells={updatesHeadCells}
      data={updatesData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
