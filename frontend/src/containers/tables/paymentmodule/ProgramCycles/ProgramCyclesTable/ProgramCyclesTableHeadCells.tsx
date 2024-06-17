import { AllProgramCyclesQuery } from '../../../../../__generated__/graphql';
import { HeadCell } from '../../../../../components/core/Table/EnhancedTableHead';

export const headCells: HeadCell<
  AllProgramCyclesQuery['allProgramCycles']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Programme Cycle ID',
    id: 'id',
    numeric: false,
    dataCy: 'id',
  },
  {
    disablePadding: false,
    label: 'Programme Cycle Title',
    id: 'title',
    numeric: false,
    dataCy: 'id',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    dataCy: 'status',
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity (USD)',
    id: 'total_delivered_quantity_usd',
    numeric: true,
    dataCy: 'total_delivered_quantity',
  },
  {
    disablePadding: false,
    label: 'Start Date',
    id: 'start_date',
    numeric: false,
    dataCy: 'start_date',
  },
  {
    disablePadding: false,
    label: 'End Date',
    id: 'end_date',
    numeric: false,
    dataCy: 'end_date',
  },
];
