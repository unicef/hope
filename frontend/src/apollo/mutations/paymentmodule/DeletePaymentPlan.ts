import { gql } from 'apollo-boost';

export const DELETE_PAYMENT_PLAN = gql`
  mutation DeletePP($paymentPlanId: ID!) {
    deletePaymentPlan(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
      }
    }
  }
`;
