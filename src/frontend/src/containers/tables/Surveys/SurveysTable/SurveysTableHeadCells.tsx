import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { Survey } from '@restgenerated/models/Survey';

export const headCells: HeadCell<Survey>[] = [
  {
    disablePadding: false,
    label: 'Survey ID',
    id: 'unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Survey Title',
    id: 'title',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Category',
    id: 'category',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Number of Recipients',
    id: 'number_of_recipients',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Created by',
    id: 'created_by',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Creation Date',
    id: 'created_at',
    numeric: false,
  },
];
