import { gql } from 'apollo-boost';

export const PAYMENT_LIST_QUERY = gql`
  query AllPayments ($paymentPlanId: String!) {
    allPayments (paymentPlanId: $paymentPlanId) {
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
        }
      }
    }
  }
`;
