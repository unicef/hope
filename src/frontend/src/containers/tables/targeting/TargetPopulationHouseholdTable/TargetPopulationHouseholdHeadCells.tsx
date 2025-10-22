import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PendingPayment } from '@restgenerated/models/PendingPayment';

export const headCells: HeadCell<PendingPayment>[] = [
  {
    disablePadding: false,
    label: 'ID',
    id: 'unicef_id',
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
    label: 'Household Size',
    id: 'size',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'admin_area__name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Score',
    id: 'household_selection__vulnerability_score',
    numeric: false,
  },
];
