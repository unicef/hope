import { gql } from 'apollo-boost';

export const query = gql`
  query PaymentVerificationPlan($id: ID!) {
    paymentVerificationPlan(id: $id) {
      id
      # cashPlan{
      #   id
      #   caHashId
      # }
    }
  }
`;
