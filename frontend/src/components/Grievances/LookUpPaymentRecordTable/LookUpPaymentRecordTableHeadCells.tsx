import { HeadCell } from '../../table/EnhancedTableHead';
import { PaymentRecordNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<PaymentRecordNode>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'cashAssistId',
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
    label: 'Cash Plan Name',
    id: 'headOfHousehold',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Delivered',
    id: 'payment_record__delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Received',
    id: 'receivedAmount',
    numeric: true,
  },
];
