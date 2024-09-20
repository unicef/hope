import { gql } from '@apollo/client';

export const GlobalAreaCharts = gql`
  query GlobalAreaCharts($year: Int!) {
    chartTotalTransferredCashByCountry(year: $year) {
      datasets {
        data
        label
      }
      labels
    }
  }
`;
