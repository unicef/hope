import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { ProgramNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<ProgramNode>[] = [
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
    id: 'totalNumberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Budget (USD)',
    id: 'budget',
    numeric: true,
  },
];
