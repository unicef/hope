import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { RegistrationDataImportNode } from '@generated/graphql';

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
    disablePadding: false,
    label: 'Is Deduplicated?',
    id: 'isDeduplicated',
    numeric: false,
    disableSort: true,
  },
  {
    disablePadding: true,
    label: 'Num. of People',
    id: 'numberOfIndividuals',
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
