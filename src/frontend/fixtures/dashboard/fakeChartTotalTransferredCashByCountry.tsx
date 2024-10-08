import { GlobalAreaChartsQuery } from '../../src/__generated__/graphql';

export const fakeChartTotalTransferredCashByCountry = {
  datasets: [
    {
      data: [1719],
      label: 'Actual cash transferred',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [0],
      label: 'Actual voucher transferred',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [1719],
      label: 'Total transferred',
      __typename: '_DetailedDatasetsNode',
    },
  ],
  labels: ['Afghanistan'],
  __typename: 'ChartDetailedDatasetsNode',
} as GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
