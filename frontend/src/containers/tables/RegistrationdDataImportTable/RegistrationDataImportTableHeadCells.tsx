import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { RegistrationDataImportNode, } from '../../../__generated__/graphql';

export const headCells: HeadCell<RegistrationDataImportNode>[] = [
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
    label: 'Num. of Households',
    id: 'numberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Imported by',
    id: 'importedBy__first_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Data Source',
    id: 'dataSource',
    numeric: false,
  },
];
