import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { HouseholdNode } from '../../../../__generated__/graphql';

export const headCells: HeadCell<HouseholdNode>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'sanctionListPossibleMatch',
    numeric: false,
    dataCy: 'sanction-list-possible-match',
  },
  {
    disablePadding: false,
    label: 'Household Id',
    id: 'unicefId',
    numeric: false,
    dataCy: 'household-id',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    dataCy: 'status',
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
    label: 'Administrative Level 2',
    id: 'admin_area__name',
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
    id: 'totalCashReceived',
    numeric: true,
    dataCy: 'household-total-cash-received',
  },
  {
    disablePadding: false,
    label: 'Registration Date',
    id: 'firstRegistrationDate',
    numeric: true,
    dataCy: 'household-registration-date',
  },
];
