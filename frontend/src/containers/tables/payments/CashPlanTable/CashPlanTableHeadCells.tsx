import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { CashPlanAndPaymentPlanNode } from '@generated/graphql';

export const headCells: HeadCell<CashPlanAndPaymentPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Payment Plan ID',
    id: 'unicef_id',
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
    label: 'Num. of Payments',
    id: 'total_number_of_households',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: 'currency_order',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'total_entitled_quantity_order',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'total_delivered_quantity_order',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'total_undelivered_quantity_order',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: 'dispersion_date',
    numeric: false,
  },
];
