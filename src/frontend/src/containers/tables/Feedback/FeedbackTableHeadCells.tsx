import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { FeedbackList } from '@restgenerated/models/FeedbackList';

export const headCells: HeadCell<FeedbackList>[] = [
  {
    disablePadding: false,
    label: 'Feedback ID',
    id: 'unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Issue Type',
    id: 'issue_type',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household_lookup',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Linked Grievance',
    id: 'linked_grievance',
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
