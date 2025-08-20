import { BlackLink } from '@components/core/BlackLink';
import React, { useState, ReactElement } from 'react';
import { TableCell, Checkbox } from '@mui/material';
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
    id: 'templateId',
    numeric: false,
    disablePadding: false,
    label: 'Template ID',
    dataCy: 'head-cell-template-id',
  },
  {
    id: 'templateName',
    numeric: false,
    disablePadding: false,
    label: 'Template Name',
    dataCy: 'head-cell-template-name',
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
  const { businessArea: businessAreaSlug, programId, baseUrl } = useBaseUrl();
  const [selected, setSelected] = useState<string[]>([]);
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
  const allIds = results.map((row: any) => row.templateId);

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
      key={row.templateId}
      data-cy={`pending-approval-row-${row.templateId}`}
    >
      <TableCell padding="checkbox">
        <Checkbox
          checked={selected.includes(row.templateId)}
          onChange={() => handleSelectOne(row.templateId)}
          inputProps={{ 'aria-label': `select row ${row.templateId}` }}
        />
      </TableCell>
      <TableCell>
        <BlackLink
          to={`/${baseUrl}/population/individuals/online-templates/${row.templateId}`}
        >
          {row.templateId}
        </BlackLink>
      </TableCell>
      <TableCell>{row.templateName}</TableCell>
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
              inputProps={{ 'aria-label': 'select all rows' }}
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
      data={results}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      title="Pending Periodic Data Updates for Approval"
      onSelectAllClick={handleSelectAllClick}
      numSelected={selected.length}
      customHeadRenderer={customHeadRenderer}
      hidePagination={true}
    />
  );
};

export default PeriodicDataUpdatePendingForApproval;
