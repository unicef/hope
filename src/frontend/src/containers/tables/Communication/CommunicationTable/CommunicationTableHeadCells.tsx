import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import type { MessageList } from '@restgenerated/models/MessageList';

export const headCells: HeadCell<MessageList>[] = [
  {
    disablePadding: false,
    label: 'Message ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Title',
    id: 'title',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Number of Recipients',
    id: 'numberOfRecipients',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Created by',
    id: 'created_by',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Creation Date',
    id: 'created_at',
    numeric: false,
  },
];
