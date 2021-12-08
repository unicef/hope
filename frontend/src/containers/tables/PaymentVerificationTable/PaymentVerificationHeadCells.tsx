import { HeadCell } from '../../../components/Table/EnhancedTableHead';
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
    id: 'serviceProvider__fullName',
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
