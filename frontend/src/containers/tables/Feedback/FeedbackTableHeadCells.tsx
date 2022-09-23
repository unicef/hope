import { HeadCell } from '../../../components/core/Table/EnhancedTableHead';
import { FeedbackNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<FeedbackNode>[] = [
  {
    disablePadding: false,
    label: 'Feedback ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Issue Type',
    id: 'issueType',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'numberOfRecipients',
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
    id: 'creation_date',
    numeric: false,
  },
];
