import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { HouseholdNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<HouseholdNode>[] = [
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'householdCaId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'paymentRecords',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'familySize',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'location',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Residence Status',
    id: 'residenceStatus',
    numeric: true,
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
