import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { CashPlanNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'cashAssistId',
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
    id: 'numberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: 'currency',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'totalEntitledQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'totalDeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'totalUndeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: 'dispersionDate',
    numeric: false,
  },
];