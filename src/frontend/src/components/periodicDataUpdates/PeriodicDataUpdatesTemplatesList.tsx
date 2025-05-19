import { fetchPeriodicDataUpdateTemplates } from '@api/periodicDataUpdateApi';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import GetAppIcon from '@mui/icons-material/GetApp';
import UploadIcon from '@mui/icons-material/Upload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { IconButton, TableCell, Tooltip } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useState } from 'react';
import { PeriodicDataUpdatesTemplateDetailsDialog } from './PeriodicDataUpdatesTemplateDetailsDialog';
import {
  useDownloadPeriodicDataUpdateTemplate,
  useExportPeriodicDataUpdateTemplate,
} from './PeriodicDataUpdatesTemplatesListActions';
import { StatusBox } from '@core/StatusBox';
import { periodicDataUpdateTemplateStatusToColor } from '@utils/utils';
import { useSnackbar } from '@hooks/useSnackBar';
import { useTranslation } from 'react-i18next';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { PeriodicDataUpdateTemplateList } from '@restgenerated/models/PeriodicDataUpdateTemplateList';

const templatesHeadCells: HeadCell<PeriodicDataUpdateTemplateList>[] = [
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
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
    dataCy: 'head-cell-status',
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
  const { t } = useTranslation();
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const permissions = usePermissions();
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(
    null,
  );

  const { mutate: exportTemplate, error: exportError } =
    useExportPeriodicDataUpdateTemplate();
  const { showMessage } = useSnackbar();

  useEffect(() => {
    if (exportError) {
      // @ts-ignore
      const message = exportError?.data?.error || exportError.message;
      showMessage(message);
    }
  }, [exportError, showMessage]);

  const handleExportClick = (templateId: number) => {
    exportTemplate({
      businessAreaSlug,
      programId,
      templateId: templateId.toString(),
    });
  };

  const handleDialogOpen = (template: PeriodicDataUpdateTemplateList) => {
    setSelectedTemplateId(template.id);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedTemplateId(null);
  };

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

  const canExportOrDownloadTemplate = hasPermissions(
    PERMISSIONS.PDU_TEMPLATE_DOWNLOAD,
    permissions,
  );

  const renderTemplateRow = (
    row: PeriodicDataUpdateTemplateList,
  ): ReactElement => (
    <ClickableTableRow key={row.id} data-cy={`template-row-${row.id}`}>
      <TableCell data-cy={`template-id-${row.id}`}>{row.id}</TableCell>
      <TableCell data-cy={`template-records-${row.id}`} align="right">
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
      <TableCell data-cy={`template-status-${row.id}`}>
        <StatusBox
          status={row.status}
          statusToColor={periodicDataUpdateTemplateStatusToColor}
        />
      </TableCell>
      <TableCell data-cy={`template-action-${row.id}`}>
        {row.status === 'EXPORTED' ? (
          <Tooltip
            title={
              row?.number_of_records === 0
                ? t('There are no records available')
                : ''
            }
          >
            <span>
              <ButtonTooltip
                variant="contained"
                color="primary"
                startIcon={<GetAppIcon />}
                data-cy={`download-btn-${row.id}`}
                href={`/api/rest/${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${row.id}/download/`}
                disabled={
                  row?.number_of_records === 0 || !canExportOrDownloadTemplate
                }
              >
                Download
              </ButtonTooltip>
            </span>
          </Tooltip>
        ) : row.can_export ? (
          <ButtonTooltip
            variant="contained"
            color="primary"
            onClick={() => handleExportClick(row.id)}
            startIcon={<UploadIcon />}
            data-cy={`export-btn-${row.id}`}
            disabled={!canExportOrDownloadTemplate}
          >
            Export
          </ButtonTooltip>
        ) : null}
      </TableCell>
    </ClickableTableRow>
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
