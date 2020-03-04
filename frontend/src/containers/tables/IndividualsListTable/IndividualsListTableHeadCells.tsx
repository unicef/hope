import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { IndividualNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<IndividualNode>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Individual',
    id: 'fullName',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household__id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Age',
    id: '-dob',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Sex',
    id: 'sex',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'household__location__title',
    numeric: false,
  },
];