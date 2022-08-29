import { HeadCell } from '../../../core/Table/EnhancedTableHead';
import { AllHouseholdsQuery } from '../../../../__generated__/graphql';

export const headCells: HeadCell<
  AllHouseholdsQuery['allHouseholds']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'radio',
    numeric: false,
    dataCy: 'radio-id',
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
    label: 'Head of Household',
    id: 'head_of_household__full_name',
    numeric: false,
    dataCy: 'household-full-name',
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
    label: 'Admin Level 2',
    id: 'admin_area__name',
    numeric: false,
    dataCy: 'household-admin-level-2',
  },
  {
    disablePadding: false,
    label: 'Programme',
    id: 'program__id',
    numeric: false,
    dataCy: 'household-programme-id',
  },
  {
    disablePadding: false,
    label: 'Registration Date',
    id: 'last_registration_date',
    numeric: false,
    dataCy: 'household-last-registration-date',
  },
];
