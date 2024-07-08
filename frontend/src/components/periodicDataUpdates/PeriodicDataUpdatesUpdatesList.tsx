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

interface Update {
  importId: string;
  templateId: string;
  importDate: string;
  importedBy: string;
  status: string;
}

const updatesHeadCells: HeadCell<Update>[] = [
  { id: 'importId', numeric: false, disablePadding: false, label: 'Import ID' },
  {
    id: 'templateId',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
  },
  {
    id: 'importDate',
    numeric: false,
    disablePadding: false,
    label: 'Import Date',
  },
  {
    id: 'importedBy',
    numeric: false,
    disablePadding: false,
    label: 'Imported by',
  },
  { id: 'status', numeric: false, disablePadding: false, label: 'Status' },
];

const renderUpdateRow = (row: Update): ReactElement => (
  <ClickableTableRow>
    <TableCell>
      <BlackLink>{row.importId}</BlackLink>
    </TableCell>
    <TableCell>
      <BlackLink>{row.templateId}</BlackLink>
    </TableCell>
    <TableCell>
      <UniversalMoment>{row.importDate}</UniversalMoment>
    </TableCell>
    <TableCell>{row.importedBy}</TableCell>
    <TableCell>
      <StatusBox
        status={statusChoices[row.status]}
        statusToColor={periodicDataUpdatesUpdatesStatusToColor}
      />
    </TableCell>
  </ClickableTableRow>
);

export const PeriodicDataUpdatesUpdatesList = (): ReactElement => {
  const initialQueryVariables = {
    page: 1,
    page_size: 10,
    ordering: 'importDate',
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: updatesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['updates', queryVariables],
    queryFn: () => fetchPeriodicDataUpdateUpdates(queryVariables), // Implement fetchPeriodicDataUpdateUpdates function based on your API
  });

  return (
    <UniversalRestTable
      isOnPaper
      renderRow={renderUpdateRow}
      headCells={updatesHeadCells}
      queryFn={() => fetchPeriodicDataUpdateUpdates(queryVariables)}
      data={updatesData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
