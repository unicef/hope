import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { AllPaymentPlansForTableQuery } from '../../../../__generated__/graphql';

export const headCells: HeadCell<
  AllPaymentPlansForTableQuery['allPaymentPlans']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Payment Plan ID',
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
    label: 'No. of Households',
    id: 'totalHouseholdsCount',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: 'currency',
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
    label: 'Total Delivered Quantity',
    id: 'totalDeliveredQuantity',
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
    label: 'Dispersion Start Date',
    id: 'dispersionStartDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Dispersion End Date',
    id: 'dispersionEndDate',
    numeric: false,
  },
];
