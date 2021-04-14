import { gql } from 'apollo-boost';

export const AllPaymentRecords = gql`
  query AllPaymentRecords(
    $cashPlan: ID
    $household: ID
    $after: String
    $before: String
    $orderBy: String
    $first: Int
    $last: Int
    $businessArea: String
  ) {
    allPaymentRecords(
      cashPlan: $cashPlan
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
          id
          createdAt
          updatedAt
          fullName
          statusDate
          status
          caId
          totalPersonsCovered
          household {
            id
            unicefId
            size
          }
          currency
          entitlementQuantity
          deliveredQuantity
          deliveredQuantityUsd
          deliveryDate
          cashPlan {
            id
            program {
              id
              name
            }
          }
        }
      }
      totalCount
      edgeCount
    }
  }
`;
