import { HeadCell } from '../../../../components/table/EnhancedTableHead';
import { TargetPopulationNode } from '../../../../__generated__/graphql';

export const headCells: HeadCell<TargetPopulationNode>[] = [
    {
      disablePadding: false,
      label: 'Id',
      id: 'id',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Final List',
      id: 'status',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Head of Household',
      id: 'head_of_household__full_name',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Household size',
      id: 'size',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Admin Level',
      id: 'adminLevel',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Location',
      id: 'admin_area__title',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Last Inspection',
      id: 'lastEditedAt',
      numeric: false,
    },
  ];