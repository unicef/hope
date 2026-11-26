import type { HeadCell } from '@components/core/Table/EnhancedTableHead';
import type { PaymentListList } from '@restgenerated/models/PaymentListList';

export const headCells: HeadCell<PaymentListList>[] = [
  {
    disablePadding: false,
    label: 'Payment List ID',
    id: 'unicefId',
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
    label: 'Num. of Households',
    id: 'totalHouseholdsCount',
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
    label: 'Dispersion Start Date',
    id: 'dispersionStartDate',
    numeric: false,
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion End Date',
    id: 'dispersionEndDate',
    numeric: false,
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Linked Payment Lists',
    id: 'followup-id',
    numeric: false,
  },
];
