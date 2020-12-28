import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { UserNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<UserNode>[] = [
  {
    disablePadding: false,
    label: 'Date',
    id: 'date',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'User',
    id: 'user',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Module',
    id: 'module',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Object',
    id: 'object',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Action',
    id: 'action',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Change From',
    id: 'changeFrom',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Change To',
    id: 'changeTo',
    numeric: false,
  },
];
