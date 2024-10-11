import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UserNode } from '@generated/graphql';

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
    label: 'Last Login',
    id: 'lastLogin',
    numeric: false,
  },
];
