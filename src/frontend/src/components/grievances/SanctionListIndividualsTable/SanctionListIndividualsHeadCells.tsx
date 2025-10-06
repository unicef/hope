import { HeadCell } from '@core/Table/EnhancedTableHead';
import { SanctionListIndividual } from '@restgenerated/models/SanctionListIndividual';

export const headCells: HeadCell<SanctionListIndividual>[] = [
  {
    disablePadding: false,
    label: 'Ref. No. on Sanction List',
    id: 'referenceNumber',
    numeric: false,
    dataCy: 'refNo',
  },
  {
    disablePadding: false,
    label: 'Full Name',
    id: 'fullName',
    numeric: false,
    dataCy: 'fullName',
  },
  {
    disablePadding: false,
    label: 'Dates of Birth',
    id: 'datesOfBirth',
    numeric: false,
    dataCy: 'datesOfBirth',
  },
  {
    disablePadding: false,
    label: 'National Ids',
    id: 'documents',
    numeric: false,
    dataCy: 'documents',
  },
];
