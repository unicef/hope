import { gql } from 'apollo-boost';

export const CountryCharts = gql`
  query CountryCharts(
    $businessAreaSlug: String!
    $year: Int!
    $program: String
    $administrativeArea: String
    $order: String
    $orderBy: String
  ) {
    tableTotalCashTransferredByAdministrativeArea(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
      order: $order
      orderBy: $orderBy
    ) {
      data {
        id
        admin2
        totalCashTransferred
        totalHouseholds
      }
    }
  }
`;
