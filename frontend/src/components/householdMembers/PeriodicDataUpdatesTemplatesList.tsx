import { TableCell } from '@mui/material';
import React, { ReactElement } from 'react';
import { UniversalRestTable, HeadCell } from 'your-path-to-components'; // replace with the actual path
import { Template, QueryVariables } from 'your-path-to-types'; // replace with the actual path

// Define the columns for the Templates table
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

// Define the renderRow function for the Templates table
const renderTemplateRow = (row: Template): ReactElement => (
  <>
    <TableCell>{row.templateId}</TableCell>
    <TableCell>{row.numberOfRecords}</TableCell>
    <TableCell>{row.creationDate}</TableCell>
    <TableCell>{row.createdBy}</TableCell>
    <TableCell>{row.details}</TableCell>
    <TableCell></TableCell>
  </>
);

// Use the UniversalRestTable component to create the Templates table
const PeriodicDataUpdatesTemplatesList = (): ReactElement => (
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

export default PeriodicDataUpdatesTemplatesList;
