import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import GetAppIcon from '@mui/icons-material/GetApp';
import UploadIcon from '@mui/icons-material/Upload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { IconButton, TableCell, Tooltip } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { periodicDataUpdateTemplateStatusToColor } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { PeriodicDataUpdatesTemplateDetailsDialog } from './PeriodicDataUpdatesTemplateDetailsDialog';
import { useExportPeriodicDataUpdateTemplate } from './PeriodicDataUpdatesTemplatesListActions';
import { PaginatedPDUXlsxTemplateListList } from '@restgenerated/models/PaginatedPDUXlsxTemplateListList';
import { PDUXlsxTemplateList } from '@restgenerated/models/PDUXlsxTemplateList';

const templatesHeadCells: HeadCell<PDUXlsxTemplateList>[] = [
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'ID',
    dataCy: 'head-cell-template-id',
  },
  {
    id: 'name',
    numeric: false,
    disablePadding: false,
    label: 'Name',
    dataCy: 'head-cell-template-name',
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

export const PeriodicDataUpdatesOfflineTemplates = (): ReactElement => {
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
      programSlug: programId,
      templateId: templateId,
    });
  };

  const handleDialogOpen = (template: PDUXlsxTemplateList) => {
    setSelectedTemplateId(template.id);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedTemplateId(null);
  };

  const initialQueryVariables = useMemo(
    () => ({
      ordering: '-created_at',
      businessAreaSlug,
      programSlug: programId,
    }),
    [businessAreaSlug, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: templatesData,
    isLoading,
    error,
  } = useQuery<PaginatedPDUXlsxTemplateListList>({
    queryKey: [
      'periodicDataUpdateTemplates',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesList(
        createApiParams(
          { businessAreaSlug, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  const selectedTemplate = templatesData?.results?.find(
    (template) => template.id === selectedTemplateId,
  );

  const canExportOrDownloadTemplate = hasPermissions(
    PERMISSIONS.PDU_TEMPLATE_DOWNLOAD,
    permissions,
  );

  const renderTemplateRow = (row: PDUXlsxTemplateList): ReactElement => (
    <ClickableTableRow key={row.id} data-cy={`template-row-${row.id}`}>
      <TableCell data-cy={`template-id-${row.id}`}>{row.id}</TableCell>
      <TableCell data-cy={`template-name-${row.id}`}>{row.name}</TableCell>
      <TableCell data-cy={`template-records-${row.id}`} align="right">
        {row.numberOfRecords}
      </TableCell>
      <TableCell data-cy={`template-created-at-${row.id}`}>
        <UniversalMoment>{row.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell data-cy={`template-created-by-${row.id}`}>
        {row.createdBy}
      </TableCell>
      <TableCell data-cy={`template-details-btn-${row.id}`}>
        <IconButton color="primary" onClick={() => handleDialogOpen(row)}>
          <VisibilityIcon />
        </IconButton>
      </TableCell>
      <TableCell data-cy={`template-status-${row.id}`}>
        <StatusBox
          status={row.status}
          statusDisplay={row.statusDisplay}
          statusToColor={periodicDataUpdateTemplateStatusToColor}
        />
      </TableCell>
      <TableCell data-cy={`template-action-${row.id}`}>
        {row.status === 'EXPORTED' ? (
          <Tooltip
            title={
              row?.numberOfRecords === 0
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
                href={`/api/rest/business-areas/${businessAreaSlug}/programs/${programId}/periodic-data-update-templates/${row.id}/download/`}
                disabled={
                  row?.numberOfRecords === 0 || !canExportOrDownloadTemplate
                }
              >
                Download
              </ButtonTooltip>
            </span>
          </Tooltip>
        ) : row.canExport ? (
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
        isOnPaper={true}
        renderRow={renderTemplateRow}
        headCells={templatesHeadCells}
        data={templatesData ?? {}}
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
