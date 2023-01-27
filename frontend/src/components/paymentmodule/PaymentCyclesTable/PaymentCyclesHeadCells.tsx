import { HeadCell } from '../../core/Table/EnhancedTableHead';
import { AllPaymentCyclesForTableQuery } from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllPaymentCyclesForTableQuery['allPaymentPlans']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Payment Cycle ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Title',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'totalEntitledQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'totalUndeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'totalDeliveredQuantity',
    numeric: true,
  },

  {
    disablePadding: false,
    label: 'Start Date',
    id: 'startDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'End Date',
    id: 'endDate',
    numeric: false,
  },
];
