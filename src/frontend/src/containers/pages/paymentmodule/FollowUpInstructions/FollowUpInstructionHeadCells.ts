import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { FollowUpInstructionList } from '@restgenerated/models/FollowUpInstructionList';

export const headCells: HeadCell<FollowUpInstructionList>[] = [
  {
    disablePadding: false,
    label: 'Instruction ID',
    id: 'unicefId',
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
    label: 'Action',
    id: 'backgroundActionStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Payment Plans',
    id: 'childPaymentPlansCount',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Households',
    id: 'householdsCount',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Entitled',
    id: 'totalEntitledQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered',
    id: 'totalDeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered',
    id: 'totalUndeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Creation Date',
    id: 'createdAt',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Modified Date',
    id: 'updatedAt',
    numeric: false,
  },
];
