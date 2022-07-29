import { gql } from 'apollo-boost';

export const PAYMENT_LIST_QUERY = gql`
  query AllPayments($paymentPlanId: String!) {
    payment(id: $id) {
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
`;
