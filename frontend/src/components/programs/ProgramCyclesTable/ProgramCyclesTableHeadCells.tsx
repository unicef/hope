import { HeadCell } from '../../core/Table/EnhancedTableHead';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Programme Cycle ID',
    id: 'id',
    numeric: false,
    dataCy: 'id',
  },
  {
    disablePadding: false,
    label: 'Programme Cycle Title',
    id: 'title',
    numeric: false,
    dataCy: 'id',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'title',
    numeric: false,
    dataCy: 'status',
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'total_entitled_quantity',
    numeric: true,
    dataCy: 'total_entitled_quantity',
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'total_undelivered_quantity',
    numeric: true,
    dataCy: 'total_undelivered_quantity',
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'total_delivered_quantity',
    numeric: true,
    dataCy: 'total_delivered_quantity',
  },
  {
    disablePadding: false,
    label: 'Start Date',
    id: 'start_date',
    numeric: false,
    dataCy: 'start_date',
  },
  {
    disablePadding: false,
    label: 'End Date',
    id: 'end_date',
    numeric: false,
    dataCy: 'end_date',
  },
  {
    disablePadding: false,
    label: '',
    id: 'edit',
    numeric: false,
    dataCy: 'edit',
    disableSort: true,
  },
  {
    disablePadding: false,
    label: '',
    id: 'remove',
    numeric: false,
    dataCy: 'remove',
    disableSort: true,
  },
];
