import { HeadCell } from '../../../../components/table/EnhancedTableHead';
import { FieldAttributeNode } from '../../../../__generated__/graphql';

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
