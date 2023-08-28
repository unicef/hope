import { HeadCell } from '../../core/Table/EnhancedTableHead';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'ID',
    id: 'id',
    numeric: false,
    dataCy: 'id',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    dataCy: 'status',
  },
];
