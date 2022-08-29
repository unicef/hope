import { AllIndividualsQuery } from '../../../../__generated__/graphql';
import { HeadCell } from '../../../core/Table/EnhancedTableHead';

export const headCells: HeadCell<
  AllIndividualsQuery['allIndividuals']['edges'][number]['node']
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
    label: 'Individual ID',
    id: 'unicefId',
    numeric: false,
    dataCy: 'individual-id',
  },
  {
    disablePadding: false,
    label: 'Full Name',
    id: 'fullName',
    numeric: false,
    dataCy: 'individual-name',
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household__id',
    numeric: false,
    dataCy: 'household-id',
  },
  {
    disablePadding: false,
    label: 'Age',
    id: '-birthDate',
    numeric: true,
    dataCy: 'individual-age',
  },
  {
    disablePadding: false,
    label: 'Gender',
    id: 'sex',
    numeric: false,
    dataCy: 'individual-sex',
  },
  {
    disablePadding: false,
    label: 'Admin Level 2',
    id: 'household__admin_area__name',
    numeric: false,
    dataCy: 'individual-location',
  },
  {
    disablePadding: false,
    label: 'Programme',
    id: 'household__programme',
    numeric: false,
    dataCy: 'individual-programme',
  },
  {
    disablePadding: false,
    label: 'Registration Date',
    id: 'individual__last-registraton-date',
    numeric: false,
    dataCy: 'individual-location',
  },
];
