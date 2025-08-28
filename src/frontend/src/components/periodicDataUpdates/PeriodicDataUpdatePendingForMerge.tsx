import React, { useState, ReactElement } from 'react';
import { TableCell, Checkbox, Button, Tooltip } from '@mui/material';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUOnlineEditListList } from '@restgenerated/models/PaginatedPDUOnlineEditListList';
import {
  periodicDataUpdatesOnlineEditsStatusToColor,
  showApiErrorMessages,
} from '@utils/utils';
import { useNavigate } from 'react-router-dom';
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

const PeriodicDataUpdatePendingForMerge = () => {
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const canMerge = hasPermissions(PERMISSIONS.PDU_ONLINE_MERGE, permissions);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { businessArea: businessAreaSlug, programId, baseUrl } = useBaseUrl();
  const [selected, setSelected] = useState<string[]>([]);
  const initialQueryVariables = {
    ordering: 'created_at',
    businessAreaSlug,
    programSlug: programId,
    status: ['APPROVED' as const],
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  const { mutateAsync: bulkMerge } = useMutation({
    mutationFn: (ids: number[]) => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsBulkMergeCreate(
        {
          businessAreaSlug,
          programSlug: programId,
          requestBody: { ids },
        },
      );
    },
    onSuccess: () => {
      showMessage('Templates merged successfully.');
      setSelected([]);
      queryClient.invalidateQueries({
        queryKey: [
          'periodicDataUpdatePendingForMerge',
          queryVariables,
          businessAreaSlug,
          programId,
        ],
      });
      queryClient.invalidateQueries({
        queryKey: [
          'mergedPeriodicDataUpdates',
          {
            ordering: 'created_at',
            businessAreaSlug,
            programSlug: programId,
            status: ['MERGED' as const],
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

  const handleMerge = async () => {
    const ids = selected.map((id) => Number(id)).filter((id) => !isNaN(id));
    await bulkMerge(ids);
  };

  const { data, isLoading, error } = useQuery<PaginatedPDUOnlineEditListList>({
    queryKey: [
      'periodicDataUpdatePendingForMerge',
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
  const allIds = results.map((row: any) => row.id);

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelected(allIds);
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
      <TableCell padding="checkbox" onClick={(e) => e.stopPropagation()}>
        {row.isAuthorized ? (
          <Checkbox
            checked={selected.includes(row.id)}
            onChange={(e) => {
              e.stopPropagation();
              handleSelectOne(row.id);
            }}
            slotProps={{ input: { 'aria-label': `select row ${row.id}` } }}
          />
        ) : (
          <Tooltip title="You are not within authorized users for this Edit">
            <span>
              <Checkbox
                checked={selected.includes(row.id)}
                disabled
                slotProps={{ input: { 'aria-label': `select row ${row.id}` } }}
              />
            </span>
          </Tooltip>
        )}
      </TableCell>
      <TableCell>
        <BlackLink
          to={`/${baseUrl}/population/individuals/online-templates/${row.id}`}
          data-cy={`template-id-link-${row.id}`}
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
          statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
        />
      </TableCell>
    </ClickableTableRow>
  );

  // Custom head renderer for EnhancedTableHead
  const customHeadRenderer = ({
    headCells,
  }: {
    headCells: HeadCell<any>[];
  }) => (
    <thead>
      <tr>
        {headCells.map((headCell) => (
          <TableCell
            key={String(headCell.id)}
            padding={headCell.id === 'checkbox' ? 'checkbox' : undefined}
          >
            {headCell.id === 'checkbox' ? (
              <Checkbox
                indeterminate={
                  selected.length > 0 && selected.length < results.length
                }
                checked={
                  selected.length > 0 && selected.length === results.length
                }
                onChange={handleSelectAllClick}
                slotProps={{ input: { 'aria-label': 'select all rows' } }}
              />
            ) : (
              headCell.label
            )}
          </TableCell>
        ))}
      </tr>
    </thead>
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
      title="Periodic Data Updates pending for Merge"
      onSelectAllClick={handleSelectAllClick}
      numSelected={selected.length}
      customHeadRenderer={customHeadRenderer}
      hidePagination={true}
      actions={
        canMerge
          ? [
              <Button
                key="merge-selected"
                variant="outlined"
                color="primary"
                onClick={handleMerge}
                disabled={selected.length === 0}
                sx={{ mr: 1 }}
              >
                Merge
              </Button>,
            ]
          : []
      }
    />
  );
};

export default PeriodicDataUpdatePendingForMerge;
