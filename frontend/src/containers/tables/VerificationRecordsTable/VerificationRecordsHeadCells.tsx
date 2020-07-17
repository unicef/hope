import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { PaymentVerificationNodeEdge } from '../../../__generated__/graphql';

export const headCells: HeadCell<PaymentVerificationNodeEdge>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Verification Status',
    id: 'verificationStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'headOfHousehold',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'householdId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Delivered Amount',
    id: 'deliveredAmount',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Received Amount',
    id: 'receivedAmount',
    numeric: false,
  },
];
