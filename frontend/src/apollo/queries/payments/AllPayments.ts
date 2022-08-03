import { gql } from 'apollo-boost';

export const AllPayments = gql`
  query AllPayments ($paymentPlanId: String!, $businessArea: String!) {
    allPayments (paymentPlanId: $paymentPlanId, businessArea: $businessArea) {
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
          household {
            id
            size
            admin2 {
              id
              name
            }
          }
          status
          currency
          entitlementDate
          entitlementQuantityUsd
          createdAt
        }
      }
    }
  }
`;
