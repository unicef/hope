<<<<<<< HEAD:frontend/src/containers/tables/programs/ProgrammesTable/ProgrammesHeadCells.tsx
import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { ProgramNode } from '../../../../__generated__/graphql';
=======
import { AllProgramsQuery } from '../../../__generated__/graphql';
import { HeadCell } from '../../../components/core/Table/EnhancedTableHead';
>>>>>>> cb4319bb4d0d695656d0ec4956559438fdd72937:frontend/src/containers/tables/ProgrammesTable/ProgrammesHeadCells.tsx

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
