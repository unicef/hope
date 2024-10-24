import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { FieldAttributeNode } from '@generated/graphql';

export const headCells: HeadCell<FieldAttributeNode>[] = [
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
