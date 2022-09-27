import { gql } from 'apollo-boost';

export const query = gql`
  query CashPlanPaymentVerification($id: ID!) {
    cashPlanPaymentVerification(id: $id) {
      id
      # cashPlan{
      #   id
      #   caHashId
      # }
    }
  }
`;
