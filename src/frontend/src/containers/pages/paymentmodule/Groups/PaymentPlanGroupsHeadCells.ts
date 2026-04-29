import { HeadCell } from '@components/core/Table/EnhancedTableHead';

type GroupRow = {
  id: string;
  name: string;
  unicefId: string;
  cycle: string;
  status: string;
};

export const headCells: HeadCell<GroupRow>[] = [
  {
    disablePadding: false,
    label: 'Name',
    id: 'name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Group ID',
    id: 'unicefId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Cycle',
    id: 'cycle',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status', // TODO: no status field on PaymentPlanGroup yet — placeholder until API is ready
    id: 'status',
    numeric: false,
  },
];
