import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { IndividualMinimalFragment } from '@generated/graphql';

export const headCells: HeadCell<IndividualMinimalFragment>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Individual',
    id: 'full_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Role',
    id: 'role',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Relationship to HoH',
    id: 'relationship',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Date of Birth',
    id: 'birthDate',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Gender',
    id: 'sex',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Dedupe within Batch',
    id: 'deduplicationBatchStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Dedupe against Population',
    id: 'deduplicationGoldenRecordStatus',
    numeric: false,
  },
];
