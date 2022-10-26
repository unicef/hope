import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { PaymentRecordNode } from '../../../../__generated__/graphql';

export const headCells: HeadCell<PaymentRecordNode>[] = [
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
    id: 'cash_plan__program__name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement Quantity',
    id: 'entitlement__entitlement_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivered Quantity',
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
