import { HeadCell } from '@core/Table/EnhancedTableHead';
import { ProgramCycle } from '@api/programCycleApi';

const headCells: HeadCell<ProgramCycle>[] = [
  {
    id: 'title',
    numeric: false,
    disablePadding: false,
    label: 'Programme Cycle Title',
    dataCy: 'head-cell-programme-cycle-title',
  },
  {
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
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

export default headCells;
