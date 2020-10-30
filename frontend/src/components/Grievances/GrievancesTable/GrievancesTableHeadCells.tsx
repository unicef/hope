import { HeadCell } from '../../table/EnhancedTableHead';
import { GrievanceTicketNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<GrievanceTicketNode>[] = [
  {
    disablePadding: false,
    label: 'Ticket Id',
    id: 'id',
    numeric: false,
    dataCy: 'ticket-id',
  },
];
