import { BlackLink } from '@components/core/BlackLink';
import React, { useState, ReactElement } from 'react';
import {
  TableCell,
  Checkbox,
  Button,
  Tooltip,
  TableHead,
  TableRow,
} from '@mui/material';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUOnlineEditListList } from '@restgenerated/models/PaginatedPDUOnlineEditListList';
import {
  periodicDataUpdatesOnlineEditsStatusToColor,
  showApiErrorMessages,
} from '@utils/utils';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';

const pendingHeadCells: HeadCell<any>[] = [
  {
    id: 'checkbox',
    numeric: false,
    disablePadding: true,
    label: '',
    dataCy: 'head-cell-checkbox',
    disableSort: true,
  },
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
    dataCy: 'head-cell-id',
  },
  {
    id: 'name',
    numeric: false,
    disablePadding: false,
    label: 'Template Name',
    dataCy: 'head-cell-name',
  },
  {
    id: 'numberOfRecords',
    numeric: true,
    disablePadding: false,
    label: 'Number of Records',
    dataCy: 'head-cell-number-of-records',
  },
  {
    id: 'createdAt',
    numeric: false,
    disablePadding: false,
    label: 'Creation Date',
    dataCy: 'head-cell-creation-date',
  },
  {
    id: 'createdBy',
    numeric: false,
    disablePadding: false,
    label: 'Created by',
    dataCy: 'head-cell-created-by',
  },
  {
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
    dataCy: 'head-cell-status',
  },
];

const PeriodicDataUpdatePendingForApproval = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const canApprove = hasPermissions(
    PERMISSIONS.PDU_ONLINE_APPROVE,
    permissions,
  );

  const { businessArea: businessAreaSlug, programId, baseUrl } = useBaseUrl();
  const [selected, setSelected] = useState<string[]>([]);
  const initialQueryVariables = {
    ordering: 'created_at',
    businessAreaSlug,
    programSlug: programId,
    status: ['READY' as const],
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  const { mutateAsync: bulkApprove } = useMutation({
    mutationFn: (ids: number[]) => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsBulkApproveCreate(
        {
          businessAreaSlug,
          programSlug: programId,
          requestBody: { ids },
        },
      );
    },
    onSuccess: () => {
      showMessage(t('Templates approved successfully.'));
      setSelected([]);
      queryClient.invalidateQueries({
        queryKey: [
          'periodicDataUpdatePendingForApproval',
          queryVariables,
          businessAreaSlug,
          programId,
        ],
      });
      queryClient.invalidateQueries({
        queryKey: [
          'periodicDataUpdatePendingForMerge',
          {
            ordering: 'created_at',
            businessAreaSlug,
            programSlug: programId,
            status: ['APPROVED' as const],
          },
          businessAreaSlug,
          programId,
        ],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const handleApprove = async() => {
    const ids = selected.map((id) => Number(id)).filter((id) => !isNaN(id));
    await bulkApprove(ids);
  };

  const { data, isLoading, error } = useQuery<PaginatedPDUOnlineEditListList>({
    queryKey: [
      'periodicDataUpdatePendingForApproval',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsList({
        businessAreaSlug,
        programSlug: programId,
        ordering: queryVariables.ordering,
        status: queryVariables.status,
      }),
    enabled: !!queryVariables.businessAreaSlug && !!queryVariables.programSlug,
  });

  const results = data?.results ?? [];
  const authorizedIds = results
    .filter((row: any) => row.isAuthorized)
    .map((row: any) => row.id);

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    // If indeterminate (some selected, not all), clicking should deselect all
    if (selected.length > 0 && selected.length < authorizedIds.length) {
      setSelected([]);
      return;
    }
    // Otherwise, toggle all
    if (event.target.checked) {
      setSelected(authorizedIds);
    } else {
      setSelected([]);
    }
  };

  const handleSelectOne = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const renderRow = (row: any): ReactElement => (
    <ClickableTableRow
      key={row.id}
      data-cy={`pending-approval-row-${row.id}`}
      onClick={() =>
        navigate(
          `/${baseUrl}/population/individuals/online-templates/${row.id}`,
        )
      }
      style={{ cursor: 'pointer' }}
    >
      <TableCell padding="checkbox">
        {row.isAuthorized ? (
          <Checkbox
            checked={selected.includes(row.id)}
            onChange={() => handleSelectOne(row.id)}
            onClick={(e) => e.stopPropagation()}
            slotProps={{ input: { 'aria-label': `select row ${row.id}` } }}
          />
        ) : (
          <Tooltip title="You are not within authorized users for this Edit">
            <span>
              <Checkbox
                checked={selected.includes(row.id)}
                disabled
                onClick={(e) => e.stopPropagation()}
                slotProps={{ input: { 'aria-label': `select row ${row.id}` } }}
              />
            </span>
          </Tooltip>
        )}
      </TableCell>
      <TableCell>
        <BlackLink
          to={`/${baseUrl}/population/individuals/online-templates/${row.id}`}
        >
          {row.id}
        </BlackLink>
      </TableCell>
      <TableCell>{row.name}</TableCell>
      <TableCell>{row.numberOfRecords}</TableCell>
      <TableCell>
        <UniversalMoment>{row.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell>{row.createdBy}</TableCell>
      <TableCell>
        <StatusBox
          status={row.status}
          statusDisplay={row.statusDisplay}
          statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
        />
      </TableCell>
    </ClickableTableRow>
  );

  const customHeadRenderer = ({
    headCells,
  }: {
    headCells: HeadCell<any>[];
  }) => (
    <TableHead>
      <TableRow>
        {headCells.map((headCell) => (
          <TableCell
            key={String(headCell.id)}
            padding={headCell.id === 'checkbox' ? 'checkbox' : undefined}
          >
            {headCell.id === 'checkbox' ? (
              <Checkbox
                indeterminate={
                  selected.length > 0 && selected.length < authorizedIds.length
                }
                checked={
                  selected.length > 0 &&
                  selected.length === authorizedIds.length
                }
                onChange={handleSelectAllClick}
                slotProps={{ input: { 'aria-label': 'select all rows' } }}
              />
            ) : (
              <div style={{ fontSize: 12 }}>{headCell.label}</div>
            )}
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );

  return (
    <UniversalRestTable
      isOnPaper={true}
      renderRow={renderRow}
      headCells={pendingHeadCells}
      data={data ?? []}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      title="Periodic Data Updates pending for Approval"
      numSelected={selected.length}
      customHeadRenderer={customHeadRenderer}
      hidePagination={true}
      actions={
        canApprove
          ? [
              <Button
                key="approve-selected"
                variant="outlined"
                color="primary"
                onClick={handleApprove}
                disabled={selected.length === 0}
                sx={{ mr: 1 }}
              >
                {t('Approve')}
              </Button>,
            ]
          : []
      }
    />
  );
};

export default PeriodicDataUpdatePendingForApproval;
