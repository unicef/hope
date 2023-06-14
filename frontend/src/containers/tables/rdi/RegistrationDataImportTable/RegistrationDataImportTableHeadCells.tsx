import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { RegistrationDataImportNode } from '../../../../__generated__/graphql';

export const headCells: HeadCell<RegistrationDataImportNode>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'radio',
    numeric: false,
    dataCy: 'radio-id',
  },
  {
    disablePadding: false,
    label: 'Title',
    id: 'name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Import Date',
    id: 'importDate',
    numeric: false,
  },
  {
    disablePadding: true,
    label: 'Num. of Individuals',
    id: 'numberOfIndividuals',
    numeric: true,
  },
  {
    disablePadding: true,
    label: 'Num. of Households',
    id: 'numberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Imported by',
    id: 'imported_by__first_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Data Source',
    id: 'data_source',
    numeric: false,
  },
];
