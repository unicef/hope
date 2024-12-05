import { gql } from '@apollo/client';

export const DeletePaymentPlan = gql`
  mutation DeletePaymentPlan($paymentPlanId: ID!) {
    deletePaymentPlan(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
      }
    }
  }
`;
