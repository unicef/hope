import { gql } from '@apollo/client';

export const UPDATE_PAYMENT_PLAN = gql`
  mutation UpdatePP($input: UpdatePaymentPlanInput!) {
    updatePaymentPlan(input: $input) {
      paymentPlan {
        id
      }
    }
  }
`;
