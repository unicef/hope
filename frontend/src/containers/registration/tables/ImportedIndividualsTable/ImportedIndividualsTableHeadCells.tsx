import { HeadCell } from '../../../../components/table/EnhancedTableHead';
import { ImportedIndividualMinimalFragment } from '../../../../__generated__/graphql';

export const headCells: HeadCell<ImportedIndividualMinimalFragment>[] = [
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
    label: 'Relationship',
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
