import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { HouseholdNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<HouseholdNode>[] = [
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'id',
    numeric: false,
    dataCy: 'household-id',
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'head_of_household__full_name',
    numeric: false,
    dataCy: 'household-head-name',
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'size',
    numeric: false,
    dataCy: 'household-size',
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'admin_area__title',
    numeric: false,
    dataCy: 'household-location',
  },
  {
    disablePadding: false,
    label: 'Residence Status',
    id: 'residenceStatus',
    numeric: false,
    dataCy: 'household-residence-status',
  },
  {
    disablePadding: false,
    label: 'Total Cash Received',
    id: 'totalCash',
    numeric: true,
    dataCy: 'household-total-cash-received',
  },
  {
    disablePadding: false,
    label: 'Registration Date',
    id: 'registrationDate',
    numeric: true,
    dataCy: 'household-registration-date',
  },
];
