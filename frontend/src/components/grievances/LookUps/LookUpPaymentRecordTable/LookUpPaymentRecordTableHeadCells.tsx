import { HeadCell } from '../../../core/Table/EnhancedTableHead';
import { PaymentRecordAndPaymentNode } from '../../../../__generated__/graphql';

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
    id: 'payment_record__parent__program__name',
    numeric: false,
    disableSort: true,
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
