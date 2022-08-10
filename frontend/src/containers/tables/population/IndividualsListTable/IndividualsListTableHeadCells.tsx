import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { IndividualNode } from '../../../../__generated__/graphql';

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
    id: 'household__unicef_id',
    numeric: false,
    dataCy: 'household-id',
  },
  {
    disablePadding: false,
    label: 'Relationship to HoH',
    id: 'relationship',
    numeric: false,
    dataCy: 'relationship',
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
    label: 'Administrative Level 2',
    id: 'household__admin_area__name',
    numeric: false,
    dataCy: 'individual-location',
  },
];
