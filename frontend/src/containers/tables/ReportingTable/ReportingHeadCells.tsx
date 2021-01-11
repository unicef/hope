import React from 'react';
import { HeadCell } from '../../../components/table/EnhancedTableHead';

export const headCells = [
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
    label: 'Creation Date',
    id: 'created_at',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Created By',
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
