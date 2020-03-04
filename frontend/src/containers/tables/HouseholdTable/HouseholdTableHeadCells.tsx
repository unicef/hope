import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { HouseholdNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<HouseholdNode>[] = [
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'head_of_household__full_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'familySize',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'location__title',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Residence Status',
    id: 'residenceStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Cash Received',
    id: 'paymentRecords',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Registration Date',
    id: 'createdAt',
    numeric: true,
  },
];
