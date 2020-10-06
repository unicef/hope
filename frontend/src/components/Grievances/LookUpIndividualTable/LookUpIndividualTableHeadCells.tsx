import { IndividualNode } from '../../../__generated__/graphql';
import { HeadCell } from '../../table/EnhancedTableHead';

export const headCells: HeadCell<IndividualNode>[] = [
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
    label: 'Location',
    id: 'household__admin_area__title',
    numeric: false,
    dataCy: 'individual-location',
  },
];
