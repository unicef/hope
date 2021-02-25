import { gql } from 'apollo-boost';

export const GlobalAreaCharts = gql`
  query GlobalAreaCharts(
    $year: Int!
  ) {
    chartTotalTransferredCashByCountry(year: $year) {
      datasets {
        data
        label
      }
      labels
    }
  }
`;
