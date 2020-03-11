import { HeadCell } from '../../../../components/table/EnhancedTableHead';
import {
  ImportedHouseholdMinimalFragment, ImportedIndividualMinimalFragment,
  RegistrationDataImportNode,
} from '../../../../__generated__/graphql';

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
    label: 'Employment/Education',
    id: 'workStatus',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Date of Birth',
    id: 'dob',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Sex',
    id: 'sex',
    numeric: false,
  },
];
