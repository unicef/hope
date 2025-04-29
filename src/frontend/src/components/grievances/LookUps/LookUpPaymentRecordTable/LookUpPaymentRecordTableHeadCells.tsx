import { HeadCell } from '@core/Table/EnhancedTableHead';
import { PaymentList } from '@restgenerated/models/PaymentList';

export const headCells: HeadCell<PaymentList>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'caId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Payment Record Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Programme Name',
    id: 'parent__program__name',
    numeric: false,
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Delivered',
    id: 'delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Received',
    id: 'payment_verification__received_amount',
    disableSort: true,
    numeric: true,
  },
];
