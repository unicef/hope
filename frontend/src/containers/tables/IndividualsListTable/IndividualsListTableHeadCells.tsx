import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { IndividualNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<IndividualNode>[] = [
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
    id: 'id',
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
    label: 'Sex',
    id: 'sex',
    numeric: false,
    dataCy: 'individual-sex',
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'household__admin_area__title',
    numeric: false,
    dataCy: 'individual-location',
  },
];
