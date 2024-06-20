import { Button, IconButton, TableCell } from '@mui/material';
import { ReactElement } from 'react';
import VisibilityIcon from '@mui/icons-material/Visibility';
import UploadIcon from '@mui/icons-material/Upload';
import GetAppIcon from '@mui/icons-material/GetApp';

import { UniversalRestTable, HeadCell } from 'your-path-to-components'; // replace with the actual path
import { Template, QueryVariables } from 'your-path-to-types'; // replace with the actual path

const templatesHeadCells: HeadCell<Template>[] = [
  {
    id: 'templateId',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
  },
  {
    id: 'numberOfRecords',
    numeric: true,
    disablePadding: false,
    label: 'Number of Records',
  },
  {
    id: 'creationDate',
    numeric: false,
    disablePadding: false,
    label: 'Creation Date',
  },
  {
    id: 'createdBy',
    numeric: false,
    disablePadding: false,
    label: 'Created by',
  },
  { id: 'details', numeric: false, disablePadding: false, label: 'Details' },
  { id: 'empty', numeric: false, disablePadding: false, label: '' },
];

const renderTemplateRow = (row: Template): ReactElement => (
  <>
    <TableCell>{row.templateId}</TableCell>
    <TableCell>{row.numberOfRecords}</TableCell>
    <TableCell>{row.creationDate}</TableCell>
    <TableCell>{row.createdBy}</TableCell>
    <TableCell>
      <IconButton color="primary">
        <VisibilityIcon />
      </IconButton>
    </TableCell>
    <TableCell>
      {row.status === 'download' ? (
        <Button variant="contained" color="primary" startIcon={<GetAppIcon />}>
          Download
        </Button>
      ) : (
        <Button variant="contained" color="primary" startIcon={<UploadIcon />}>
          Export
        </Button>
      )}
    </TableCell>
  </>
);

export const PeriodicDataUpdatesTemplatesList = (): ReactElement => (
  <UniversalRestTable<Template, QueryVariables>
    initialVariables={
      {
        /* initial query variables */
      }
    }
    endpoint="templates" // replace with the actual endpoint
    queriedObjectName="templates" // replace with the actual object name
    renderRow={renderTemplateRow}
    headCells={templatesHeadCells}
    title="Templates"
    queryFn={/* query function */}
    queryKey={['templates']} // replace with the actual query key
  />
);
