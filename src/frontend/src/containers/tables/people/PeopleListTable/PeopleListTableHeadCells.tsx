import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { IndividualList } from '@restgenerated/models/IndividualList';

export const headCells: HeadCell<IndividualList>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'sanctionListPossibleMatch',
    numeric: false,
    dataCy: 'sanction-list-possible-match',
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
    label: 'Individual',
    id: 'fullName',
    numeric: false,
    dataCy: 'individual-name',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    dataCy: 'status',
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Type',
    id: 'type',
    numeric: false,
    dataCy: 'individual-age',
  },
  {
    disablePadding: false,
    label: 'Age',
    id: 'birthDate',
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
    label: 'Administrative Level 2',
    id: 'household__admin_area__name',
    numeric: false,
    dataCy: 'individual-location',
  },
];
