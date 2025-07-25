import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { HouseholdList } from '@restgenerated/models/HouseholdList';

export const headCells: HeadCell<HouseholdList>[] = [
  {
    disablePadding: false,
    label: '',
    id: '',
    numeric: false,
  },
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
    id: 'size',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'admin2_title',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Data Collected',
    id: 'first_registration_date',
    numeric: false,
  },
];
