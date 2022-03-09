import { AllChartsQuery } from '../../src/__generated__/graphql';

export const fakeChartIndividualsReachedByAgeAndGender = {
  datasets: [
    { data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], __typename: '_DatasetsNode' },
  ],
  labels: [
    'Females 0-5',
    'Females 6-11',
    'Females 12-17',
    'Females 18-59',
    'Females 60+',
    'Males 0-5',
    'Males 6-11',
    'Males 12-17',
    'Males 18-59',
    'Males 60+',
  ],
  __typename: 'ChartDatasetNode',
} as AllChartsQuery['chartIndividualsReachedByAgeAndGender'];
