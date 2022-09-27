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
    id: 'unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Id',
    id: 'household_id',
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
    id: 'admin2',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Collector',
    id: 'collector_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Payment Channel',
    id: 'assigned_payment_channel',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'FSP',
    id: 'financial_service_provider__name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement (USD)',
    id: 'entitlement_quantity_usd',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Delivered Quantity',
    id: 'delivered_quantity',
    numeric: false,
  },
];
