import { gql } from 'apollo-boost';

export const UPDATE_PAYMENT_PLAN = gql`
  mutation UpdatePP($input: UpdatePaymentPlanInput!) {
    updatePaymentPlan(input: $input) {
      paymentPlan {
        id
      }
    }
  }
`;
