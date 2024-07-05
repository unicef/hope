import { Button, IconButton, TableCell } from '@mui/material';
import { ReactElement, useState } from 'react';
import VisibilityIcon from '@mui/icons-material/Visibility';
import UploadIcon from '@mui/icons-material/Upload';
import GetAppIcon from '@mui/icons-material/GetApp';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { fetchPeriodicDataUpdateTemplates } from '@api/periodicDataUpdate';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';

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
  {
    id: 'details',
    numeric: false,
    disablePadding: false,
    label: 'Details',
    disableSort: true,
  },
  {
    id: 'empty',
    numeric: false,
    disablePadding: false,
    label: '',
    disableSort: true,
  },
];

const renderTemplateRow = (row: Template): ReactElement => (
  <ClickableTableRow>
    <TableCell>{row.id}</TableCell>
    <TableCell>{row.number_of_records}</TableCell>
    <TableCell>
      <UniversalMoment>{row.created_at}</UniversalMoment>
    </TableCell>
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
  </ClickableTableRow>
);

export const PeriodicDataUpdatesTemplatesList = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();

  const initialQueryVariables = {
    page: 1,
    page_size: 10,
    ordering: 'created_at',
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: templatesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: [
      'periodicDataUpdateTemplates',
      businessAreaSlug,
      programId,
      queryVariables,
    ],
    queryFn: () =>
      fetchPeriodicDataUpdateTemplates(
        businessAreaSlug,
        programId,
        queryVariables,
      ),
  });

  return (
    <UniversalRestTable
      renderRow={renderTemplateRow}
      headCells={templatesHeadCells}
      title="Templates"
      queryFn={() =>
        fetchPeriodicDataUpdateTemplates(businessAreaSlug, programId)
      }
      data={templatesData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
