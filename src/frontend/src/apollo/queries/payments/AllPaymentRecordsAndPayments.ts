import { gql } from '@apollo/client';

export const AllPaymentRecordsAndPayments = gql`
  query AllPaymentRecordsAndPayments(
    $household: ID
    $after: String
    $before: String
    $orderBy: String
    $first: Int
    $last: Int
    $businessArea: String!
    $program: String
  ) {
    allPaymentRecordsAndPayments(
      household: $household
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
      program: $program
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
          unicefId
          currency
          entitlementQuantity
          deliveredQuantity
          deliveredQuantityUsd
          deliveryDate
          parent {
            id
            programName
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
