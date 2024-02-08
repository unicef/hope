import { AllProgramsQuery } from '@generated/graphql';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';

export const headCells: HeadCell<
  AllProgramsQuery['allPrograms']['edges'][number]['node']
>[] = [
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
    // disabled because number_of_households is not a field in the program model
    id: 'number_of_households',
    numeric: true,
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Budget (USD)',
    id: 'budget',
    numeric: true,
  },
];
