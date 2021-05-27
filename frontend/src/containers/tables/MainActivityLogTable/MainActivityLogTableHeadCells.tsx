import {HeadCell} from '../../../components/table/EnhancedTableHead';
import {AllLogEntriesQuery} from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllLogEntriesQuery['allLogEntries']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Date',
    id: 'date',
    numeric: false,
    weight: 0.8,
  },
  {
    disablePadding: false,
    label: 'User',
    id: 'user',
    numeric: false,
    weight: 0.7,
  },
  {
    disablePadding: false,
    label: 'Entity',
    id: 'content_type__name',
    numeric: false,
    weight: 1,
  },
  {
    disablePadding: false,
    label: 'Object',
    id: 'object',
    numeric: false,
    weight: 1,
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
    label: 'Changes',
    id: 'changes',
    numeric: false,
    weight: 0.4,
  },
  {
    disablePadding: false,
    label: 'Change From',
    id: 'changeFrom',
    numeric: false,
    weight: 1,
  },
  {
    disablePadding: false,
    label: 'Change To',
    id: 'changeTo',
    numeric: false,
    weight: 1,
  },
];
