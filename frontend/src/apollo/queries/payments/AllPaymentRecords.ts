import { gql } from 'apollo-boost';

export const AllPaymentRecords = gql`
  query AllPaymentRecords(
    $parent: ID
    $household: ID
    $after: String
    $before: String
    $orderBy: String
    $first: Int
    $last: Int
    $businessArea: String
  ) {
    allPaymentRecords(
      parent: $parent
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
          headOfHousehold {
            id
            fullName
          }
          currency
          entitlementQuantity
          deliveredQuantity
          deliveredQuantityUsd
          deliveryDate
          parent {
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
