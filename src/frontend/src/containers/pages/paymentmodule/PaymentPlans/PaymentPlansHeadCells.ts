import type { HeadCell } from '@components/core/Table/EnhancedTableHead';
import type { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';

export const headCells: HeadCell<PaymentPlanList>[] = [
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'cycle',
    numeric: false,
    weight: 25,
  },
  {
    disablePadding: false,
    label: 'Name',
    id: 'name',
    numeric: false,
    weight: 25,
  },
  {
    disablePadding: false,
    label: 'Payment Plan ID',
    id: 'unicefId',
    numeric: false,
    weight: 25,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    weight: 25,
  },
];
