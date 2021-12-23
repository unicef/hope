import { HeadCell } from '../../Table/EnhancedTableHead';
import { AllSanctionListIndividualsQuery } from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllSanctionListIndividualsQuery['allSanctionListIndividuals']['edges'][number]['node']
>[] = [
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
  {
    disablePadding: false,
    label: 'Listed On',
    id: 'listedOn',
    numeric: false,
    dataCy: 'listedOn',
  },
];
