import { HeadCell } from '@core/Table/EnhancedTableHead';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';

const headCells: HeadCell<ProgramCycleList>[] = [
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
    id: 'total_entitled_quantity_usd',
    numeric: true,
    disablePadding: false,
    label: 'Total Entitled Quantity (USD)',
    disableSort: true,
    dataCy: 'head-cell-total-entitled-quantity_usd',
  },
  {
    id: 'total_undelivered_quantity_usd',
    numeric: true,
    disablePadding: false,
    label: 'Total Undelivered Quantity (USD)',
    disableSort: true,
    dataCy: 'head-cell-total-undelivered-quantity_usd',
  },
  {
    id: 'total_delivered_quantity_usd',
    numeric: true,
    disablePadding: false,
    label: 'Total Delivered Quantity (USD)',
    disableSort: true,
    dataCy: 'head-cell-total-delivered-quantity_usd',
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
