import { gql } from 'apollo-boost';

export const AllCashPlans = gql`
  query AllCashPlans(
    $program: ID!
    $after: String
    $before: String
    $count: Int
    $orderBy: String
  ) {
    allCashPlans(
      program: $program
      after: $after
      before: $before
      first: $count
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
          cashAssistId
          numberOfHouseholds
          disbursementDate
          currency
          status
          totalEntitledQuantity
          totalDeliveredQuantity
          totalUndeliveredQuantity
        }
      }
    }
  }
`;
