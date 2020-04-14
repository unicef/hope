import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { TargetPopulationNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<TargetPopulationNode>[] = [
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
      label: 'No. of Households Candidate List',
      id: 'candidateListTotalHouseholds',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'No. of Households Final List',
      id: 'finalListTotalHouseholds',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Date Created',
      id: 'createdAt',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Last edited',
      id: 'lastEditedAt',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Created by',
      id: 'createdByName',
      numeric: false,
    },
  ];