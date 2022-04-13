import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { AllCashPlansQuery } from '../../../../__generated__/graphql';

export const headCells: HeadCell<
  AllCashPlansQuery['allCashPlans']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Payment Plan ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'No. of Households',
    id: '',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: '',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: '',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Deliverd Quantity',
    id: '',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: '',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: '',
    numeric: false,
  },
];
