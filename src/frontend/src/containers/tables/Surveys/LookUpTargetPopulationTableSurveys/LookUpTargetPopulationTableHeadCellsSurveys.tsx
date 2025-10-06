import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';

export const headCells: HeadCell<TargetPopulationList>[] = [
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
    label: 'Num. of Households',
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
    label: 'Last Edited',
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
