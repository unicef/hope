import { fetchPeriodicDataUpdateTemplates } from '@api/periodicDataUpdateApi';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import GetAppIcon from '@mui/icons-material/GetApp';
import UploadIcon from '@mui/icons-material/Upload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { Button, IconButton, TableCell } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { PeriodicDataUpdatesTemplateDetailsDialog } from './PeriodicDataUpdatesTemplateDetailsDialog';
import {
  useDownloadPeriodicDataUpdateTemplate,
  useExportPeriodicDataUpdateTemplate,
} from './PeriodicDataUpdatesTemplatesListActions';

export interface Template {
  id: number;
  number_of_records: number;
  created_at: string;
  created_by: string;
  status: string;
}

const templatesHeadCells: HeadCell<Template>[] = [
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
    dataCy: 'head-cell-template-id',
  },
  {
    id: 'number_of_records',
    numeric: true,
    disablePadding: false,
    label: 'Number of Records',
    dataCy: 'head-cell-number-of-records',
  },
  {
    id: 'created_at',
    numeric: false,
    disablePadding: false,
    label: 'Creation Date',
    dataCy: 'head-cell-created-at',
  },
  {
    id: 'created_by',
    numeric: false,
    disablePadding: false,
    label: 'Created by',
    dataCy: 'head-cell-created-by',
  },
  {
    id: 'details',
    numeric: false,
    disablePadding: false,
    label: 'Details',
    disableSort: true,
    dataCy: 'head-cell-details',
  },
  {
    id: 'empty',
    numeric: false,
    disablePadding: false,
    label: '',
    disableSort: true,
    dataCy: 'head-cell-empty',
  },
];

export const PeriodicDataUpdatesTemplatesList = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(
    null,
  );

  const { mutate: downloadTemplate } = useDownloadPeriodicDataUpdateTemplate();
  const { mutate: exportTemplate } = useExportPeriodicDataUpdateTemplate();

  const handleDownloadClick = (templateId: number) => {
    downloadTemplate({
      businessAreaSlug,
      programId,
      templateId: templateId.toString(),
    });
  };

  const handleExportClick = (templateId: number) => {
    exportTemplate({
      businessAreaSlug,
      programId,
      templateId: templateId.toString(),
    });
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
    <ClickableTableRow key={row.id} data-cy={`template-row-${row.id}`}>
      <TableCell data-cy={`template-id-${row.id}`}>{row.id}</TableCell>
      <TableCell data-cy={`template-records-${row.id}`}>
        {row.number_of_records}
      </TableCell>
      <TableCell data-cy={`template-created-at-${row.id}`}>
        <UniversalMoment>{row.created_at}</UniversalMoment>
      </TableCell>
      <TableCell data-cy={`template-created-by-${row.id}`}>
        {row.created_by}
      </TableCell>
      <TableCell data-cy={`template-details-btn-${row.id}`}>
        <IconButton color="primary" onClick={() => handleDialogOpen(row)}>
          <VisibilityIcon />
        </IconButton>
      </TableCell>
      <TableCell data-cy={`template-action-${row.id}`}>
        {row.status === 'download' ? (
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleDownloadClick(row.id)}
            startIcon={<GetAppIcon />}
            data-cy={`download-btn-${row.id}`}
          >
            Download
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleExportClick(row.id)}
            startIcon={<UploadIcon />}
            data-cy={`export-btn-${row.id}`}
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
