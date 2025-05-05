import { HeadCell } from '@core/Table/EnhancedTableHead';
import { ProgramCycle } from '@api/programCycleApi';

export const headCells: HeadCell<ProgramCycle>[] = [
  {
    id: 'title',
    numeric: false,
    disablePadding: false,
    label: 'Programme Cycle Title',
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
    id: 'startDate',
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
