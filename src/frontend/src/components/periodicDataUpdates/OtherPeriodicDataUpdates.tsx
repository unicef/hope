import React, { useState, ReactElement } from 'react';
import { TableCell } from '@mui/material';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUOnlineEditListList } from '@restgenerated/models/PaginatedPDUOnlineEditListList';
import { periodicDataUpdatesOnlineEditsStatusToColor } from '@utils/utils';
import { useNavigate } from 'react-router-dom';

const otherHeadCells: HeadCell<any>[] = [
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

const OtherPeriodicDataUpdates = () => {
  const navigate = useNavigate();
  const { businessArea: businessAreaSlug, programId, baseUrl } = useBaseUrl();
  const initialQueryVariables = {
    ordering: 'created_at',
    businessAreaSlug,
    programSlug: programId,
    status: [
      'CREATING',
      'MERGING',
      'PENDING_CREATE',
      'NOT_SCHEDULED_CREATE',
      'CANCELED_CREATE',
      'NOT_SCHEDULED_MERGE',
      'CANCELED_MERGE',
      'MERGED',
      'FAILED_MERGE',
      'FAILED_CREATE',
    ] as const,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const { data, isLoading, error } = useQuery<PaginatedPDUOnlineEditListList>({
    queryKey: [
      'otherPeriodicDataUpdates',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsList({
        businessAreaSlug,
        programSlug: programId,
        ordering: queryVariables.ordering,
        status: [...queryVariables.status],
      }),
    enabled: !!queryVariables.businessAreaSlug && !!queryVariables.programSlug,
  });

  const renderRow = (row: any): ReactElement => {
    return (
      <ClickableTableRow
        key={row.id}
        data-cy={`other-row-${row.id}`}
        onClick={() =>
          navigate(
            `/${baseUrl}/population/individuals/online-templates/${row.id}`,
          )
        }
        style={{ cursor: 'pointer' }}
      >
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
  };

  return (
    <UniversalRestTable
      isOnPaper={true}
      renderRow={renderRow}
      headCells={otherHeadCells}
      data={data ?? []}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      title="Other Periodic Data Updates"
      hidePagination={true}
    />
  );
};

export default OtherPeriodicDataUpdates;
