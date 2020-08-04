import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { PaymentVerificationNodeEdge } from '../../../__generated__/graphql';

export const headCells: HeadCell<PaymentVerificationNodeEdge>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'payment_record',
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
    label: 'Head of Household',
    id: 'payment_record__household__head_of_household__family_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'payment_record__household',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Delivered Quantity',
    id: 'payment_record__delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Received Amount',
    id: 'received_amount',
    numeric: true,
  },
];
