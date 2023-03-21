import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
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
    label: 'Programme',
    id: 'parent__program__name',
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
