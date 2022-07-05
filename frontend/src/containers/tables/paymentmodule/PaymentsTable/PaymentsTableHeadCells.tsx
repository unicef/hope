import { AllGrievanceTicketQuery } from '../../../../__generated__/graphql';
import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';

export const headCells: HeadCell<
  AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'flag',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Payment Id',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Id',
    id: 'household__id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'household__size',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'household__admin2',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Collector',
    id: 'household__collector_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Payment Channel',
    id: 'payment_channel',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement (USD)',
    id: 'entitlement',
    numeric: false,
  },
];
