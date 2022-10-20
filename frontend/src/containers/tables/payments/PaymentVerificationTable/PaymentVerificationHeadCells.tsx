import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { CashPlanAndPaymentPlanNode } from '../../../../__generated__/graphql';

export const headCells: HeadCell<
  CashPlanAndPaymentPlanNode
>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'unicefId',
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
