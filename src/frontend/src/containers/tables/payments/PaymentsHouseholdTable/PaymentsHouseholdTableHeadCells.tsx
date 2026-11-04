import type { HeadCell } from '@components/core/Table/EnhancedTableHead';
import type { PaymentRow } from '@restgenerated/models/PaymentRow';

export const headCells: HeadCell<PaymentRow>[] = [
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
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Group',
    id: 'paymentPlan',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'paymentListCycle',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'hohFullName',
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
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Group',
    id: 'paymentPlan',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'paymentListCycle',
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
