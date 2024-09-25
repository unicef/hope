import { AllChartsQuery } from '../../src/__generated__/graphql';

export const fakeChartGrievances = {
  datasets: [{ data: [2, 1, 0, 0], __typename: '_DatasetsNode' }],
  labels: [
    'Resolved',
    'Unresolved',
    'Unresolved for longer than 30 days',
    'Unresolved for longer than 60 days',
  ],
  totalNumberOfGrievances: 3,
  totalNumberOfFeedback: 0,
  totalNumberOfOpenSensitive: 0,
  __typename: 'ChartGrievanceTicketsNode',
} as AllChartsQuery['chartGrievances'];
