import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { AllCashPlansQuery } from '../../../../__generated__/graphql';

export const headCells: HeadCell<
  AllCashPlansQuery['allCashPlans']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'FSP',
    id: 'fsp',
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
    label: 'Configuration Status',
    id: 'configuration_status',
    numeric: false,
  },
];
