import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { CashPlanAndPaymentPlanNode } from '@generated/graphql';

export const headCells: HeadCell<CashPlanAndPaymentPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Payment Plan ID',
    id: 'unicefId',
    numeric: false,
    dataCy: 'unicefId',
  },
  {
    disablePadding: false,
    label: 'Verification Status',
    id: 'verificationStatus',
    numeric: false,
    dataCy: 'verificationStatus',
  },
  {
    disablePadding: false,
    label: 'Cash Amount',
    id: 'totalDeliveredQuantity',
    numeric: true,
    dataCy: 'totalDeliveredQuantity',
  },
  {
    disablePadding: false,
    label: 'Timeframe',
    id: 'timeframe',
    numeric: false,
    dataCy: 'startDate',
  },
  {
    disablePadding: false,
    label: 'Last Modified Date',
    id: 'updatedAt',
    numeric: false,
    dataCy: 'updatedAt',
  },
];
