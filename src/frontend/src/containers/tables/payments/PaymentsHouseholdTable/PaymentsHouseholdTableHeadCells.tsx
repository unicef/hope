import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentList } from '@restgenerated/models/PaymentList';

export const headCells: HeadCell<PaymentList>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'unicefId',
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
    label: 'Payment Purpose',
    id: 'paymentPlanPurposes',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Group',
    id: 'paymentPlanGroup',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'paymentPlanCycle',
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

export const headCellsPeople: HeadCell<any>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'unicefId',
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
    label: 'Payment Purpose',
    id: 'paymentPlanPurposes',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Group',
    id: 'paymentPlanGroup',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'paymentPlanCycle',
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
