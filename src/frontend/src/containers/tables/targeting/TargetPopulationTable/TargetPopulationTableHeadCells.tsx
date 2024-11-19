import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { TargetPopulationNode } from '@generated/graphql';

export const headCells: HeadCell<TargetPopulationNode>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'radio',
    numeric: false,
    dataCy: 'radio-id',
  },
  {
    disablePadding: false,
    label: 'Name',
    id: 'name',
    numeric: false,
    dataCy: 'name',
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
    label: 'Num. of Households',
    id: 'total_households_count',
    numeric: false,
    dataCy: 'num-of-households',
  },
  {
    disablePadding: false,
    label: 'Date Created',
    id: 'created_at',
    numeric: false,
    dataCy: 'date-created',
  },
  {
    disablePadding: false,
    label: 'Last Edited',
    id: 'updated_at',
    numeric: false,
    dataCy: 'last-edited',
  },
  {
    disablePadding: false,
    label: 'Created by',
    id: 'created_by',
    numeric: false,
    dataCy: 'created-by',
  },
];
