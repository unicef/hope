import { gql } from 'apollo-boost';

export const AllPaymentRecordsAndPayments = gql`
  query AllPaymentRecordsAndPayments(
    $household: ID
    $after: String
    $before: String
    $orderBy: String
    $first: Int
    $last: Int
    $businessArea: String!
  ) {
    allPaymentRecordsAndPayments(
      household: $household
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          objType
          id
          fullName
          status
          caId
          currency
          entitlementQuantity
          deliveredQuantity
          deliveredQuantityUsd
          deliveryDate
          parent {
            id
            programmeName
          }
          verification {
            id
            receivedAmount
          }
        }
      }
      totalCount
    }
  }
`;
