import { gql } from '@apollo/client';

export const LookUpPaymentRecords = gql`
  query LookUpPaymentRecords(
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
          caId
          parent {
            id
            name
          }
          deliveredQuantity
        }
      }
      totalCount
      edgeCount
    }
  }
`;
