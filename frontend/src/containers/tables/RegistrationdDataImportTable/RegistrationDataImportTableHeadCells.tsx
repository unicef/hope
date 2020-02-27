import { HeadCell } from '../../../components/table/EnhancedTableHead';
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
    label: 'Status',
    id: 'status',
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
    id: 'household__household_ca_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'totalPersonCovered',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement',
    id: 'entitlement__entitlement_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivered Amount',
    id: 'entitlement__delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivery Date',
    id: 'entitlement__delivery_date',
    numeric: true,
  },
];