import { HeadCell } from '@components/core/Table/EnhancedTableHead';

export const headCells: HeadCell<any>[] = [
  {
    disablePadding: false,
    label: 'Name',
    id: 'labelEn',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Type',
    id: 'associatedWith',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Field Type',
    id: 'isFlexField',
    numeric: false,
  },
];
