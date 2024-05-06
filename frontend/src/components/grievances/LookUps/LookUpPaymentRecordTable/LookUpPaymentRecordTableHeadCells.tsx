import { HeadCell } from '@core/Table/EnhancedTableHead';
import { PaymentRecordAndPaymentNode } from '@generated/graphql';

export const headCells: HeadCell<PaymentRecordAndPaymentNode>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'caId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Verification Status',
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
