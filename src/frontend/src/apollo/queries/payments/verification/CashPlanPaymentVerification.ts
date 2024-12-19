import { gql } from '@apollo/client';

export const query = gql`
  query PaymentVerificationPlan($id: ID!) {
    paymentVerificationPlan(id: $id) {
      id
    }
  }
`;
