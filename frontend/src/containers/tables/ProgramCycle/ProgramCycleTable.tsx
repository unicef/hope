import { ProgramQuery } from '@generated/graphql';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HeadCell } from '@core/Table/EnhancedTableHead';
import React, { ReactElement, useState } from 'react';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { UniversalMoment } from '@core/UniversalMoment';
import { IconButton } from '@mui/material';
import { StatusBox } from '@core/StatusBox';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import { programCycleStatusToColor } from '@utils/utils';
import DeleteIcon from '@mui/icons-material/Delete';

interface ProgramCycleTableProps {
  program: ProgramQuery['program'];
}

interface ProgramCycle {
  id: string;
  unicef_id: string;
  title: string;
  status: string;
  total_entitled_quantity?: number;
  total_undelivered_quantity?: number;
  total_delivered_quantity?: number;
  start_date: string;
  end_date?: string;
}

const headCells: HeadCell<ProgramCycle>[] = [
  {
    id: 'unicef_id',
    numeric: false,
    disablePadding: false,
    label: 'Programme Cycles ID',
    disableSort: true,
    dataCy: 'head-cell-id',
  },
  {
    id: 'title',
    numeric: false,
    disablePadding: false,
    label: 'Programme Cycles Title',
    disableSort: true,
    dataCy: 'head-cell-programme-cycles-title',
  },
  {
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
    disableSort: true,
    dataCy: 'head-cell-status',
  },
  {
    id: 'total_entitled_quantity',
    numeric: true,
    disablePadding: false,
    label: 'Total Entitled Quantity',
    disableSort: true,
    dataCy: 'head-cell-total-entitled-quantity',
  },
  {
    id: 'total_undelivered_quantity',
    numeric: true,
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    disableSort: true,
    dataCy: 'head-cell-total-undelivered-quantity',
  },
  {
    id: 'total_delivered_quantity',
    numeric: true,
    disablePadding: false,
    label: 'Total Delivered Quantity',
    disableSort: true,
    dataCy: 'head-cell-total-delivered-quantity',
  },
  {
    id: 'start_date',
    numeric: false,
    disablePadding: false,
    label: 'Start Date',
    dataCy: 'head-cell-start-date',
  },
  {
    id: 'end_date',
    numeric: false,
    disablePadding: false,
    label: 'End Date',
    disableSort: true,
    dataCy: 'head-cell-end-date',
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

interface DataResponse {
  results: ProgramCycle[];
  count: number;
}

export const ProgramCycleTable = ({ program }: ProgramCycleTableProps) => {
  const [queryVariables, setQueryVariables] = useState({
    page: 1,
    page_size: 10,
    ordering: 'created_at',
  });

  // TODO fetch data from API
  const isLoading = false;
  const error = '';
  const data: DataResponse = {
    results: [
      {
        id: 'bc83b39a-d731-4a57-bfec-9cf2f7a65097',
        unicef_id: 'P-1',
        title: 'Default Programme Cycle',
        status: 'ACTIVE',
        total_entitled_quantity: null,
        total_undelivered_quantity: null,
        total_delivered_quantity: null,
        start_date: '01.01.2020',
        end_date: '',
      },
      {
        id: 'd81c9633-5362-4d2f-93a6-d30f92d90230',
        unicef_id: 'P-2',
        title: 'January Payments 2020',
        status: 'DRAFT',
        total_entitled_quantity: null,
        total_undelivered_quantity: null,
        total_delivered_quantity: null,
        start_date: '01.01.2020',
        end_date: '02.01.2020',
      },
      {
        id: 'b870d17d-7555-4565-86e2-69bae4fa3fd1',
        unicef_id: 'P-3',
        title: 'February Payments 2020',
        status: 'FINISHED',
        total_entitled_quantity: null,
        total_undelivered_quantity: null,
        total_delivered_quantity: null,
        start_date: '02.01.2020',
        end_date: '03.01.2020',
      },
    ],
    count: 3,
  };

  const statusChoices = {
    DRAFT: 'Draft',
    ACTIVE: 'Active',
    FINISHED: 'Finished',
  };

  const renderRow = (row: ProgramCycle): ReactElement => (
    <ClickableTableRow key={row.id} data-cy={`program-cycle-row-${row.id}`}>
      <TableCell data-cy={`program-cycle-id-${row.id}`}>
        {row.unicef_id}
      </TableCell>
      <TableCell data-cy={`program-cycle-title-${row.id}`}>
        {row.title}
      </TableCell>
      <TableCell data-cy={`program-cycle-status-${row.id}`}>
        <StatusBox
          status={statusChoices[row.status]}
          statusToColor={programCycleStatusToColor}
        />
      </TableCell>
      <TableCell data-cy={`program-cycle-total-entitled-quantity-${row.id}`}>
        {row.total_entitled_quantity ?? '-'}
      </TableCell>
      <TableCell data-cy={`program-cycle-total-undelivered-quantity-${row.id}`}>
        {row.total_undelivered_quantity ?? '-'}
      </TableCell>
      <TableCell data-cy={`program-cycle-total-delivered-quantity-${row.id}`}>
        {row.total_delivered_quantity ?? '-'}
      </TableCell>
      <TableCell data-cy={`program-cycle-start-date-${row.id}`}>
        <UniversalMoment>{row.start_date}</UniversalMoment>
      </TableCell>
      <TableCell data-cy={`program-cycle-end-date-${row.id}`}>
        <UniversalMoment>{row.end_date}</UniversalMoment>
      </TableCell>

      <TableCell data-cy={`program-cycle-details-btn-${row.id}`}>
        {(row.status === 'DRAFT' || row.status === 'ACTIVE') && (
          <IconButton color="primary" onClick={() => console.log(row)}>
            <EditIcon />
          </IconButton>
        )}

        {row.status === 'DRAFT' && (
          <IconButton color="primary" onClick={() => console.log(row)}>
            <DeleteIcon />
          </IconButton>
        )}
      </TableCell>
    </ClickableTableRow>
  );

  return (
    <UniversalRestTable
      title="Program Cycles"
      renderRow={renderRow}
      headCells={headCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
