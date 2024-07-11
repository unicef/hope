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
import { fetchPeriodicDataUpdateUpdates } from '@api/periodicDataUpdate';
import { Missing } from '@components/core/Missing';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface Update {
  id: string;
  template: string;
  created_at: string;
  created_by: string;
  status: string;
}

const updatesHeadCells: HeadCell<Update>[] = [
  { id: 'id', numeric: false, disablePadding: false, label: 'Import ID' },
  {
    id: 'template',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
  },
  {
    id: 'created_at',
    numeric: false,
    disablePadding: false,
    label: 'Import Date',
  },
  {
    id: 'created_by',
    numeric: false,
    disablePadding: false,
    label: 'Imported by',
  },
  { id: 'status', numeric: false, disablePadding: false, label: 'Status' },
];

const renderUpdateRow = (row: Update): ReactElement => (
  <ClickableTableRow>
    <TableCell>
      <BlackLink>{row.id}</BlackLink>
    </TableCell>
    <TableCell>
      <BlackLink>{row.template}</BlackLink>
    </TableCell>
    <TableCell>
      <UniversalMoment>{row.created_at}</UniversalMoment>
    </TableCell>
    <TableCell>{row.created_by}</TableCell>
    <TableCell>
      {/* <StatusBox
        status={statusChoices[row.status]}
        statusToColor={periodicDataUpdatesUpdatesStatusToColor}
      /> */}
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
