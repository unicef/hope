import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { IconButton, TableCell } from '@mui/material';
import { periodicDataUpdatesUpdatesStatusToColor } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { createApiParams } from '@utils/apiUtils';
import { useQuery } from '@tanstack/react-query';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { PeriodicDataUpdatesUploadDetailsDialog } from '@components/periodicDataUpdates/PeriodicDataUpdatesUploadDetailsDialog';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUXlsxUploadListList } from '@restgenerated/models/PaginatedPDUXlsxUploadListList';
import { PDUXlsxUploadList } from '@restgenerated/models/PDUXlsxUploadList';

const updatesHeadCells: HeadCell<PDUXlsxUploadList>[] = [
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'Import ID',
    dataCy: 'head-cell-import-id',
  },
  {
    id: 'template',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
    dataCy: 'head-cell-template-id',
  },
  {
    id: 'created_at',
    numeric: false,
    disablePadding: false,
    label: 'Import Date',
    dataCy: 'head-cell-import-date',
  },
  {
    id: 'created_by',
    numeric: false,
    disablePadding: false,
    label: 'Imported by',
    dataCy: 'head-cell-imported-by',
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
];

export const PeriodicDataUpdatesOfflineEdits = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedUploadId, setSelectedUploadId] = useState<number | null>(null);
  const initialQueryVariables = useMemo(
    () => ({
      ordering: 'created_at',
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
    data: updatesData,
    isLoading,
    error,
  } = useQuery<PaginatedPDUXlsxUploadListList>({
    queryKey: [
      'periodicDataUpdateUploads',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateUploadsList(
        createApiParams(
          { businessAreaSlug, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  const handleDialogOpen = (uploadId) => {
    setSelectedUploadId(uploadId);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedUploadId(null);
  };

  const renderUpdateRow = (row: PDUXlsxUploadList): ReactElement => (
    <ClickableTableRow key={row.id} data-cy={`update-row-${row.id}`}>
      <TableCell data-cy={`update-id-${row.id}`}>{row.id}</TableCell>
      <TableCell data-cy={`update-template-${row.id}`}>
        {row.template}
      </TableCell>
      <TableCell data-cy={`update-created-at-${row.id}`}>
        <UniversalMoment>{row.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell data-cy={`update-created-by-${row.id}`}>
        {row.createdBy}
      </TableCell>
      <TableCell data-cy={`update-details-${row.id}`}>
        {row.status === 'FAILED' ? (
          <IconButton
            data-cy={`update-details-btn-${row.id}`}
            color="primary"
            onClick={() => handleDialogOpen(row.id)}
          >
            <VisibilityIcon />
          </IconButton>
        ) : null}
      </TableCell>
      <TableCell data-cy={`update-status-${row.id}`}>
        <StatusBox
          status={row.status}
          statusToColor={periodicDataUpdatesUpdatesStatusToColor}
        />
      </TableCell>
    </ClickableTableRow>
  );

  return (
    <>
      {selectedUploadId && (
        <PeriodicDataUpdatesUploadDetailsDialog
          open={isDialogOpen}
          onClose={handleDialogClose}
          uploadId={selectedUploadId}
        />
      )}
      <UniversalRestTable
        isOnPaper={true}
        renderRow={renderUpdateRow}
        headCells={updatesHeadCells}
        data={updatesData ?? {}}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
      />
    </>
  );
};
