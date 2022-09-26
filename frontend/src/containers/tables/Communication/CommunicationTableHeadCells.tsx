import { HeadCell } from '../../../components/core/Table/EnhancedTableHead';
import { CommunicationMessageNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<CommunicationMessageNode>[] = [
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
    label: 'Number of recipients',
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
    label: 'Creation date',
    id: 'created_at',
    numeric: false,
  },
];
