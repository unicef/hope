import { HeadCell } from '../table/EnhancedTableHead';
import { LogEntryObject } from '../../__generated__/graphql';

export const headCells: HeadCell<LogEntryObject>[] = [
  {
    disablePadding: false,
    label: 'Date',
    id: 'timestamp',
    numeric: false,
    weight: 0.4,
  },
  {
    disablePadding: false,
    label: 'User',
    id: 'actor',
    numeric: false,
    weight: 0.6,
  },
  {
    disablePadding: false,
    label: 'Action',
    id: 'action',
    numeric: false,
    weight: 0.4,
  },
  {
    disablePadding: false,
    label: 'Change from',
    id: 'change_from',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Change to',
    id: 'change_to',
    numeric: false,
  },
];