import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { ProgramList } from '@restgenerated/models/ProgramList';

export const headCells: HeadCell<ProgramList>[] = [
  {
    disablePadding: false,
    label: '',
    id: '',
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
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Timeframe',
    id: 'startDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Sector',
    id: 'sector',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Num. of Households',
    id: 'totalHhCount',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Budget (USD)',
    id: 'budget',
    numeric: true,
  },
];
