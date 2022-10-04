import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { CashPlanAndPaymentPlanNode } from '../../../../__generated__/graphql';

export const headCells: HeadCell<CashPlanAndPaymentPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'ca_id',
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
    label: 'Num. of Households',
    id: 'total_number_of_hh',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: 'assistance_measurement',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'total_entitled_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'total_delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'total_undelivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: 'dispersion_date',
    numeric: false,
  },
];
