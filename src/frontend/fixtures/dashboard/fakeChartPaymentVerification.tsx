import { AllChartsQuery } from '../../src/__generated__/graphql';

export const fakeChartPaymentVerification = {
  datasets: [
    { label: 'PENDING', data: [0], __typename: '_DetailedDatasetsNode' },
    { label: 'RECEIVED', data: [0], __typename: '_DetailedDatasetsNode' },
    { label: 'NOT RECEIVED', data: [0], __typename: '_DetailedDatasetsNode' },
    {
      label: 'RECEIVED WITH ISSUES',
      data: [0],
      __typename: '_DetailedDatasetsNode',
    },
  ],
  labels: ['Payment Verification'],
  households: 0,
  averageSampleSize: 0,
  __typename: 'ChartPaymentVerification',
} as AllChartsQuery['chartPaymentVerification'];
