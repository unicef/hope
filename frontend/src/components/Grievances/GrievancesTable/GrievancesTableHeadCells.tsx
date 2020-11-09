import { HeadCell } from '../../table/EnhancedTableHead';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Ticket Id',
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
    label: 'Assigned to',
    id: 'assignedTo',
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
    label: 'Household Id',
    id: 'householdId',
    numeric: false,
    dataCy: 'householdId',
  },
  {
    disablePadding: false,
    label: 'Creation date',
    id: 'createdAt',
    numeric: false,
    dataCy: 'createdAt',
  },
  {
    disablePadding: false,
    label: 'Last modified date',
    id: 'userModified',
    numeric: false,
    dataCy: 'userModified',
  },
];
