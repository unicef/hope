import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { TableCell } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';

const onlineEditsHeadCells: HeadCell<any>[] = [
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
    dataCy: 'head-cell-empty',
  },
];

const NewPeriodicDataUpdates = (): ReactElement => {
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();
  const [queryVariables, setQueryVariables] = useState({
    ordering: 'created_at',
    businessAreaSlug,
    programSlug: programId,
  });

  // Replace with correct query and data model for online edits
  const { data, isLoading, error } = useQuery({
    queryKey: [
      'periodicDataUpdateOnlineEdits',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () => Promise.resolve([]), // TODO: Replace with actual API call
  });

  const renderRow = (row: any): ReactElement => (
    <ClickableTableRow
      key={row.templateId}
      data-cy={`online-edit-row-${row.templateId}`}
    >
      <TableCell>{row.templateId}</TableCell>
      <TableCell>{row.templateName}</TableCell>
      <TableCell>{row.numberOfRecords}</TableCell>
      <TableCell>
        <UniversalMoment>{row.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell>{row.createdBy}</TableCell>
      <TableCell>{/* Details button or info here */}</TableCell>
      <TableCell>
        <StatusBox status={row.status} statusToColor={() => 'primary'} />
      </TableCell>
      <TableCell />
    </ClickableTableRow>
  );

  return (
    <UniversalRestTable
      isOnPaper={true}
      renderRow={renderRow}
      headCells={onlineEditsHeadCells}
      data={data}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      title="New Periodic Data Updates"
      hidePagination={true}
    />
  );
};

export default NewPeriodicDataUpdates;
