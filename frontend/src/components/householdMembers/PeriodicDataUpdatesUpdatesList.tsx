import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { TableCell } from '@mui/material';
import { periodicDataUpdatesUpdatesStatusToColor } from '@utils/utils';
import { ReactElement } from 'react';
import { UniversalRestTable, HeadCell } from 'your-path-to-components'; // Adjust the path
import { Update, QueryVariables } from 'your-path-to-types'; // Adjust the path

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
  <>
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
  </>
);

export const PeriodicDataUpdatesUpdatesList = (): ReactElement => (
  <UniversalRestTable<Update, QueryVariables>
    initialVariables={
      {
        /* initial query variables */
      }
    }
    endpoint="updates" // Adjust the endpoint
    queriedObjectName="updates" // Adjust the object name
    renderRow={renderUpdateRow}
    headCells={updatesHeadCells}
    title="Updates"
    queryFn={() => {}}
    queryKey={['updates']} // Adjust the query key
  />
);
