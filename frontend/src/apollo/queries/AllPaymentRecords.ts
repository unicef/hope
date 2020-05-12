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
          createdAt
          updatedAt
          name
          statusDate
          status
          headOfHousehold
          cashAssistId
          totalPersonCovered
          household {
            id
            size
          }
          entitlement {
            id
            entitlementQuantity
            deliveredQuantity
            deliveryDate
          }
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
