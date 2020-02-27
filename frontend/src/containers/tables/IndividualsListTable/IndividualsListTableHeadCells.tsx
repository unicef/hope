import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { IndividualNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<IndividualNode>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'individualCaId',
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
    id: 'householdCaId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Age',
    id: 'age',
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
    id: 'location',
    numeric: false,
  },
];