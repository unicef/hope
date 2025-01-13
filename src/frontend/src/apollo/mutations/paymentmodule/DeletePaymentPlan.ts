import { gql } from '@apollo/client';

export const DELETE_PAYMENT_PLAN = gql`
  mutation DeletePaymentP($paymentPlanId: ID!) {
    deletePaymentPlan(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
      }
    }
  }
`;
