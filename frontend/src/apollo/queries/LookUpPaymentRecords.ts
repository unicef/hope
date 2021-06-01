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
          caId
          verifications {
            edges {
              node {
                id
                status
                receivedAmount
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
