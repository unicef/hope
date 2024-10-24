import { HeadCell } from '@core/Table/EnhancedTableHead';
import { AllGrievanceTicketQuery } from '@generated/graphql';

export const headCells: HeadCell<
AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Ticket ID',
    id: 'id',
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
    label: 'Category',
    id: 'category',
    numeric: false,
    dataCy: 'category',
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'householdId',
    numeric: false,
    dataCy: 'householdId',
  },
  {
    disablePadding: false,
    label: 'Assigned to',
    id: 'assignedTo',
    numeric: false,
    dataCy: 'assignedTo',
  },

  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'admin',
    numeric: false,
    dataCy: 'admin',
  },
];
