import { gql } from 'apollo-boost';

export const AllPaymentRecords = gql`
  query AllPaymentRecords(
    $cashPlan: ID!
    $after: String
    $before: String
    $orderBy: String
    $count: Int
  ) {
    allPaymentRecords(
      cashPlan: $cashPlan
      after: $after
      before: $before
      first: $count
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
            householdCaId
            familySize
          }
          entitlement {
            id
            entitlementQuantity
            deliveredQuantity
            deliveryDate
          }
        }
      }
      totalCount
      edgeCount
    }
  }
`;
