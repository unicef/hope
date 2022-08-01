import { gql } from 'apollo-boost';

export const PAYMENT_LIST_QUERY = gql`
  query AllPayments ($paymentPlanId: String!, $businessArea: String!) {
    allPayments (paymentPlanId: $paymentPlanId, businessArea: $businessArea) {
      edges {
        node {
          id
          household {
            id
            size
            admin2 {
              name
            }
          }
          status
          currency
          entitlementDate
          entitlementQuantityUsd
        }
      }
    }
  }
`;
