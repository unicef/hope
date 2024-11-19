import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentRecordNode } from '@generated/graphql';

export const headCells: HeadCell<PaymentRecordNode>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'ca_id',
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
    id: 'head_of_household__full_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household__unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Status',
    id: 'household__status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'household__size',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement Quantity',
    id: 'entitlement_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivered Quantity',
    id: 'delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivery Date',
    id: 'delivery_date',
    numeric: true,
  },
];
