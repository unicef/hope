import { Button, IconButton, TableCell } from '@mui/material';
import { ReactElement, useState } from 'react';
import VisibilityIcon from '@mui/icons-material/Visibility';
import UploadIcon from '@mui/icons-material/Upload';
import GetAppIcon from '@mui/icons-material/GetApp';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  downloadPeriodicDataUpdateTemplate,
  exportPeriodicDataUpdateTemplate,
  fetchPeriodicDataUpdateTemplates,
} from '@api/periodicDataUpdate';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { PeriodicDataUpdatesTemplateDetailsDialog } from './PeriodicDataUpdatesTemplateDetailsDialog';

export interface Template {
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

export const PeriodicDataUpdatesTemplatesList = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(
    null,
  );

  // Mutation for downloading a template
  const { mutate: downloadTemplate } = useMutation(
    async (templateId: string) => {
      return downloadPeriodicDataUpdateTemplate(
        businessAreaSlug,
        programId,
        templateId,
      );
    },
    {
      onSuccess: () => {
        // Handle success, e.g., show a success message
      },
      onError: (error) => {
        // Handle error, e.g., show an error message
      },
    },
  );

  // Mutation for exporting a template
  const { mutate: exportTemplate } = useMutation(
    async (templateId: string) => {
      return exportPeriodicDataUpdateTemplate(
        businessAreaSlug,
        programId,
        templateId,
      );
    },
    {
      onSuccess: () => {
        // Handle success, e.g., show a success message
      },
      onError: (error) => {
        // Handle error, e.g., show an error message
      },
    },
  );
  // Example of a direct download action, not using useQuery
  const handleDownloadClick = async () => {
    if (selectedTemplateId) {
      await downloadPeriodicDataUpdateTemplate(
        businessAreaSlug,
        programId,
        selectedTemplateId,
      );
    }
  };

  // Example of a direct export action, not using useQuery
  const handleExportClick = async () => {
    if (selectedTemplateId) {
      await exportPeriodicDataUpdateTemplate(
        businessAreaSlug,
        programId,
        selectedTemplateId,
      );
    }
  };

  const handleDialogOpen = (template: Template) => {
    setSelectedTemplateId(template.id);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedTemplateId(null);
  };

  const renderTemplateRow = (row: Template): ReactElement => (
    <ClickableTableRow>
      <TableCell>{row.id}</TableCell>
      <TableCell>{row.number_of_records}</TableCell>
      <TableCell>
        <UniversalMoment>{row.created_at}</UniversalMoment>
      </TableCell>
      <TableCell>{row.created_by}</TableCell>
      <TableCell>
        <IconButton color="primary" onClick={() => handleDialogOpen(row)}>
          <VisibilityIcon />
        </IconButton>
      </TableCell>
      <TableCell>
        {row.status === 'download' ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleDownloadClick}
            startIcon={<GetAppIcon />}
          >
            Download
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={handleExportClick}
            startIcon={<UploadIcon />}
          >
            Export
          </Button>
        )}
      </TableCell>
    </ClickableTableRow>
  );

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

  const selectedTemplate = templatesData?.results?.find(
    (template) => template.id === selectedTemplateId,
  );

  return (
    <>
      <UniversalRestTable
        isOnPaper={false}
        renderRow={renderTemplateRow}
        headCells={templatesHeadCells}
        data={templatesData}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
      />
      {selectedTemplate && (
        <PeriodicDataUpdatesTemplateDetailsDialog
          open={isDialogOpen}
          onClose={handleDialogClose}
          template={selectedTemplate}
        />
      )}
    </>
  );
};
