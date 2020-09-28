import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { ProgramNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<ProgramNode>[] = [
  {
    disablePadding: false,
    label: 'Programme',
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
    id: 'timeframe',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Frequency of Payments',
    id: 'frequencyOfPayments',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Budget',
    id: 'budget',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Population Goal',
    id: 'populationGoal',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'No. of Households',
    id: 'totalNumberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Sector',
    id: 'sector',
    numeric: false,
  },
];
