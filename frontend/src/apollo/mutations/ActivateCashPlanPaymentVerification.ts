import { gql } from 'apollo-boost';

export const ACTIVATE_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation ActivateCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
    activateCashPlanPaymentVerification(
      cashPlanVerificationId: $cashPlanVerificationId
    ) {
      cashPlan {
        id
        status
        statusDate
      }
    }
  }
`;
