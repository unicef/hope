import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PendingPayment } from '@restgenerated/models/PendingPayment';

export const headCells: HeadCell<PendingPayment>[] = [
  {
    disablePadding: false,
    label: 'ID',
    id: 'household_unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'head_of_household',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'household_size',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'household_admin2',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Score',
    id: 'vulnerability_score',
    numeric: false,
  },
];
