import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { CashPlanNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'id',
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
    id: 'assistanceThrough',
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
    id: 'programme',
    numeric: false,
  },
];
