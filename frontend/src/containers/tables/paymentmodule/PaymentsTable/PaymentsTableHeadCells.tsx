import { AllPaymentsForTableQuery } from '../../../../__generated__/graphql';
import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';

export const headCells: HeadCell<
AllPaymentsForTableQuery['allPayments']['edges'][number]['node']
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
    id: 'payment_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Id',
    id: 'payment_household__id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'payment_household__size',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'payment_household__admin2',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Collector',
    id: 'payment_household__collector_id',
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
    id: 'payment_entitlement',
    numeric: false,
  },
];
