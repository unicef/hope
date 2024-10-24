import { HeadCell } from '@core/Table/EnhancedTableHead';
import { AllGrievanceTicketQuery } from '@generated/graphql';

export const headCells: HeadCell<
AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Ticket ID',
    id: 'unicef_id',
    numeric: false,
    dataCy: 'ticket-id',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    dataCy: 'status',
  },
  {
    disablePadding: false,
    label: 'Assigned to',
    id: 'assigned_to__last_name',
    numeric: false,
    dataCy: 'assignedTo',
  },
  {
    disablePadding: false,
    label: 'Category',
    id: 'category',
    numeric: false,
    dataCy: 'category',
  },
  {
    disablePadding: false,
    label: 'Issue Type',
    id: 'issueType',
    numeric: false,
    dataCy: 'issueType',
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household_unicef_id',
    numeric: false,
    dataCy: 'householdId',
  },
  {
    disablePadding: false,
    label: 'Priority',
    id: 'priority',
    numeric: false,
    dataCy: 'priority',
  },
  {
    disablePadding: false,
    label: 'Urgency',
    id: 'urgency',
    numeric: false,
    dataCy: 'urgency',
  },
  {
    disablePadding: false,
    label: 'Linked Tickets',
    id: 'linked_tickets',
    numeric: false,
    dataCy: 'linkedTickets',
  },
  {
    disablePadding: false,
    label: 'Creation Date',
    id: 'created_at',
    numeric: false,
    dataCy: 'createdAt',
  },
  {
    disablePadding: false,
    label: 'Last Modified Date',
    id: 'user_modified',
    numeric: false,
    dataCy: 'userModified',
  },
  {
    disablePadding: false,
    label: 'Total Days',
    id: 'total_days',
    numeric: false,
    dataCy: 'totalDays',
  },
];
