import { gql } from 'apollo-boost';

export const AllCashPlans = gql`
  query AllCashPlans(
    $program: ID!
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
  ) {
    allCashPlans(
      program: $program
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edges {
        cursor
        node {
          id
          caId
          totalPersonsCovered
          dispersionDate
          assistanceMeasurement
          status
          totalEntitledQuantity
          totalDeliveredQuantity
          totalUndeliveredQuantity
        }
      }
    }
  }
`;
