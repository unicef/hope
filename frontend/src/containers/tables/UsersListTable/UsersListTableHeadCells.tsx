import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { UserNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<UserNode>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'arrow',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Name',
    id: 'lastName',
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
    label: 'Partner',
    id: 'partner',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Email',
    id: 'email',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Last login',
    id: 'lastLogin',
    numeric: false,
  },
];
