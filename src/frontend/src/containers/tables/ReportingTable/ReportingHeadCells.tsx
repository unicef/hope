import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { ReportNode } from '@generated/graphql';

export const headCells: HeadCell<ReportNode>[] = [
  {
    disablePadding: false,
    label: 'Report Type',
    id: 'report_type',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Timeframe',
    id: 'date_from',
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
    label: 'Num. of Records',
    id: 'numberOfRecords',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Creation Date',
    id: 'created_at',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Created by',
    id: 'created_by__first_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: '',
    id: '',
    numeric: false,
  },
];
