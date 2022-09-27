import { HeadCell } from '../../../components/core/Table/EnhancedTableHead';
import { FeedbackNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<FeedbackNode>[] = [
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
    id: 'linkedGrievance',
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
