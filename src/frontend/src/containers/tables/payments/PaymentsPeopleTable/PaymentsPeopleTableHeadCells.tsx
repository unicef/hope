import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentNode } from '@generated/graphql';

export const headCells: HeadCell<PaymentNode>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'internalData__caId',
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
