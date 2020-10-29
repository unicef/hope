import { gql } from 'apollo-boost';

export const LookUpPaymentRecords = gql`
  query LookUpPaymentRecords(
    $cashPlan: ID
    $household: ID
    $after: String
    $before: String
    $orderBy: String
    $first: Int
    $last: Int
  ) {
    allPaymentRecords(
      cashPlan: $cashPlan
      household: $household
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
      edges {
        cursor
        node {
          id
          caId
          verifications {
            edges {
              node {
                status
              }
            }
          }
          cashPlan {
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
