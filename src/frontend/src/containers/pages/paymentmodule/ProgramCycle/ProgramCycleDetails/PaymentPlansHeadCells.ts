import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';

export const headCells: HeadCell<PaymentPlanList>[] = [
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
    label: 'Num. of Households',
    id: 'totalHouseholdsCount',
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
    label: 'Total Undelivered Quantity',
    id: 'totalUndeliveredQuantity',
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
    label: 'Dispersion Start Date',
    id: 'dispersionStartDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Dispersion End Date',
    id: 'dispersionEndDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Follow-up Payment Plans',
    id: 'followup-id',
    numeric: false,
  },
];
