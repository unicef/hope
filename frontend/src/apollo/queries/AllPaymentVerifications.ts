import { gql } from 'apollo-boost';

export const AllPaymentVerifications = gql`
  query AllPaymentVerifications(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $cashPlanPaymentVerification: ID
  ) {
    allPaymentVerifications(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      cashPlanPaymentVerification: $cashPlanPaymentVerification
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
