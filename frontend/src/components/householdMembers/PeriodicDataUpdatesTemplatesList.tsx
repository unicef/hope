import { Button, IconButton, TableCell } from '@mui/material';
import { ReactElement } from 'react';
import VisibilityIcon from '@mui/icons-material/Visibility';
import UploadIcon from '@mui/icons-material/Upload';
import GetAppIcon from '@mui/icons-material/GetApp';
// Adjust the import path as necessary. Ensure the Template type matches the API response structure.
import { QueryVariables } from 'your-path-to-types';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { fetchPeriodicDataUpdateTemplates } from '@api/periodicDataUpdate';

// Adjusted Template type to match the API response
interface Template {
  id: number;
  number_of_records: number;
  created_at: string;
  created_by: string;
  status: string;
}

const templatesHeadCells: HeadCell<Template>[] = [
  { id: 'id', numeric: false, disablePadding: false, label: 'Template ID' },
  {
    id: 'number_of_records',
    numeric: true,
    disablePadding: false,
    label: 'Number of Records',
  },
  {
    id: 'created_at',
    numeric: false,
    disablePadding: false,
    label: 'Creation Date',
  },
  {
    id: 'created_by',
    numeric: false,
    disablePadding: false,
    label: 'Created by',
  },
  { id: 'details', numeric: false, disablePadding: false, label: 'Details' },
  { id: 'empty', numeric: false, disablePadding: false, label: '' },
];

const renderTemplateRow = (row: Template): ReactElement => (
  <>
    <TableCell>{row.id}</TableCell>
    <TableCell>{row.number_of_records}</TableCell>
    <TableCell>{row.created_at}</TableCell>
    <TableCell>{row.created_by}</TableCell>
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

export const PeriodicDataUpdatesTemplatesList = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();

  const { data: templatesData, isLoading } = useQuery({
    queryKey: ['periodicDataUpdateTemplates', businessAreaSlug, programId],
    queryFn: () =>
      fetchPeriodicDataUpdateTemplates(businessAreaSlug, programId),
  });

  return (
    <UniversalRestTable<Template, QueryVariables>
      initialVariables={{}}
      endpoint={`/api/rest/${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`}
      queriedObjectName="templates"
      renderRow={renderTemplateRow}
      headCells={templatesHeadCells}
      title="Templates"
      queryFn={() =>
        fetchPeriodicDataUpdateTemplates(businessAreaSlug, programId)
      }
      queryKey={['templates', businessAreaSlug, programId]}
      data={templatesData?.results} // Accessing the results array from the API response
      isLoading={isLoading}
    />
  );
};
