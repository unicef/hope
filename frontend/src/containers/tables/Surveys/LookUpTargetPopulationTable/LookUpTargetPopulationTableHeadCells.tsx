import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import { TargetPopulationNode } from '../../../../__generated__/graphql';

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
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Programme',
    id: 'program__id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Num. of households',
    id: 'final_list_total_households',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Date Created',
    id: 'created_at',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Last edited',
    id: 'updated_at',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Created by',
    id: 'created_by',
    numeric: false,
  },
];
