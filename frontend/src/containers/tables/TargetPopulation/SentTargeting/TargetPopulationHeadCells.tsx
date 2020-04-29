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
      label: 'Head of Household',
      id: 'headOfHousehold',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Household size',
      id: 'householdSize',
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
      id: 'location',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Last Inspection',
      id: 'lastEditedAt',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'V.Score',
      id: 'vScore',
      numeric: false,
    },
  ];