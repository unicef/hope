import { RegistrationDetailedFragment } from '../../src/__generated__/graphql';

export const fakeRegistrationDetailedFragment = {
  id: 'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl',
  createdAt: '2022-02-07T11:45:52.336426',
  name: 'romaniaks',
  status: 'MERGED',
  importDate: '2022-02-07T11:45:52.336512',
  erased: false,
  importedBy: {
    id: 'VXNlck5vZGU6OTEyZjg1MGItOWQwMS00ZTdmLWFiZDgtNjJkZTcwMjhjODY1',
    firstName: 'Maciej',
    lastName: 'Szewczyk',
    email: 'fffff@gmail.com',
    __typename: 'UserNode',
  },
  dataSource: 'XLS',
  numberOfHouseholds: 2,
  numberOfIndividuals: 6,
  __typename: 'RegistrationDataImportNode',
  datahubId: 'a5c025e4-0010-404c-8a22-515e0609d469',
  errorMessage: '',
  batchDuplicatesCountAndPercentage: [
    {
      count: 2,
      percentage: 33.33333333333333,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 2,
      percentage: 33.33333333333333,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 2,
      percentage: 33.33333333333333,
      __typename: 'CountAndPercentageNode',
    },
  ],
  batchUniqueCountAndPercentage: [
    {
      count: 4,
      percentage: 66.66666666666666,
    },
    {
      count: 4,
      percentage: 66.66666666666666,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 4,
      percentage: 66.66666666666666,
      __typename: 'CountAndPercentageNode',
    },
  ],
  goldenRecordUniqueCountAndPercentage: [
    {
      count: 6,
      percentage: 100,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 6,
      percentage: 100,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 6,
      percentage: 100,
      __typename: 'CountAndPercentageNode',
    },
  ],
  goldenRecordDuplicatesCountAndPercentage: [
    {
      count: 0,
      percentage: 0,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 0,
      percentage: 0,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 0,
      percentage: 0,
      __typename: 'CountAndPercentageNode',
    },
  ],
  goldenRecordPossibleDuplicatesCountAndPercentage: [
    {
      count: 0,
      percentage: 0,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 0,
      percentage: 0,
      __typename: 'CountAndPercentageNode',
    },
    {
      count: 0,
      percentage: 0,
      __typename: 'CountAndPercentageNode',
    },
  ],
} as RegistrationDetailedFragment;
