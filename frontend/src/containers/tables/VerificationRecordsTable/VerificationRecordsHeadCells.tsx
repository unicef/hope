import {HeadCell} from '../../../components/table/EnhancedTableHead';
import {PaymentVerificationNode} from '../../../__generated__/graphql';

export const headCells: HeadCell<PaymentVerificationNode>[] = [
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
    id: 'payment_record__household__unicef_id',
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
  {
    disablePadding: false,
    label: 'Phone #',
    id: 'payment_record__household__head_of_household__phone_no',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Alt. Phone #',
    id: 'payment_record__household__head_of_household__phone_no_alternative',
    numeric: false,
  },
];
