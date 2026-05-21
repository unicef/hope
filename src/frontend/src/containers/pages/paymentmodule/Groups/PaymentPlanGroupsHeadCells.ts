import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentPlanGroupList } from '@restgenerated/models/PaymentPlanGroupList';

export const headCells: HeadCell<PaymentPlanGroupList>[] = [
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'cycle',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Name',
    id: 'name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Group ID',
    id: 'unicefId',
    numeric: false,
  },
];
