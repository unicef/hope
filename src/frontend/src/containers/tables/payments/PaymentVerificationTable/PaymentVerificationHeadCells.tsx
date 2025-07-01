import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentPlanNode } from '@generated/graphql';

export const headCells: HeadCell<PaymentPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Payment Plan ID',
    id: 'unicefId',
    numeric: false,
    dataCy: 'unicefId',
  },
  {
    disablePadding: false,
    label: 'Payment Plan Status',
    id: 'verificationStatus',
    numeric: false,
    dataCy: 'verificationStatus',
  },
  {
    disablePadding: false,
    label: 'Total Amount',
    id: 'totalDeliveredQuantity',
    numeric: true,
    dataCy: 'totalDeliveredQuantity',
  },
  {
    disablePadding: false,
    label: 'Payment Disbursement Dates',
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
