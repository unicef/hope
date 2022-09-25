import { HeadCell } from '../../../components/core/Table/EnhancedTableHead';
import { CommunicationMessageRecipientMapNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<CommunicationMessageRecipientMapNode>[] = [
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
    label: 'Registration Date',
    id: 'firstRegistrationDate',
    numeric: true,
    dataCy: 'household-registration-date',
  },
];
