import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { AllCashPlansQuery } from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllCashPlansQuery['allCashPlans']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'caId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Verification Status',
    id: 'verificationStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'FSP',
    id: 'service_provider__full_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Modality',
    id: 'deliveryType',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Cash Amount',
    id: 'totalDeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Timeframe',
    id: 'startDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Programme',
    id: 'program__name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Last Modified Date',
    id: 'updatedAt',
    numeric: false,
  },
];
