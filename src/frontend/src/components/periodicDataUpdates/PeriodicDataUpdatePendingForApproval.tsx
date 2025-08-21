import { BlackLink } from '@components/core/BlackLink';
import React, { useState, ReactElement } from 'react';
import { TableCell, Checkbox, Button } from '@mui/material';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUOnlineEditListList } from '@restgenerated/models/PaginatedPDUOnlineEditListList';
import { periodicDataUpdatesOnlineEditsStatusToColor } from '@utils/utils';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

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
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { businessArea: businessAreaSlug, programId, baseUrl } = useBaseUrl();
  const [selected, setSelected] = useState<string[]>([]);
  const handleApprove = () => {
    // TODO: Implement approve logic for selected rows
    // Example: console.log('Approve', selected);
    alert(`Approved template IDs: ${selected.join(', ')}`);
  };
  const initialQueryVariables = {
    ordering: 'created_at',
    businessAreaSlug,
    programSlug: programId,
    status: ['READY' as const],
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

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
      <TableCell padding="checkbox">
        <Checkbox
          checked={selected.includes(row.id)}
          onChange={() => handleSelectOne(row.id)}
          slotProps={{ input: { 'aria-label': `select row ${row.id}` } }}
        />
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
      title="Pending Periodic Data Updates for Approval"
      onSelectAllClick={handleSelectAllClick}
      numSelected={selected.length}
      customHeadRenderer={customHeadRenderer}
      hidePagination={true}
      actions={[
        <Button
          key="approve-selected"
          variant="contained"
          color="primary"
          onClick={handleApprove}
          disabled={selected.length === 0}
          sx={{ mr: 1 }}
        >
          {t('Approve')}
        </Button>,
      ]}
    />
  );
};

export default PeriodicDataUpdatePendingForApproval;
