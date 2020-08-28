import { gql } from 'apollo-boost';

export const AllPaymentVerifications = gql`
  query AllPaymentVerifications(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $cashPlanPaymentVerification: ID
    $search: String
    $status: String
  ) {
    allPaymentVerifications(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      cashPlanPaymentVerification: $cashPlanPaymentVerification
      search: $search
      status: $status
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
          paymentRecord {
            id
            deliveredQuantity
            household {
              id
              headOfHousehold {
                id
                fullName
              }
            }
          }
          status
          receivedAmount
        }
      }
    }
  }
`;
