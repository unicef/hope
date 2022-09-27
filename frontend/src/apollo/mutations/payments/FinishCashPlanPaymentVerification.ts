import { gql } from 'apollo-boost';

export const FINISH_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation FinishCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
    finishCashPlanPaymentVerification(
      cashPlanVerificationId: $cashPlanVerificationId
    ) {
      cashPlan {
        id
        status
        statusDate
        # verificationPlans {
        #   edges {
        #     node {
        #       id
        #       status
        #       completionDate
        #     }
        #   }
        # }
        # paymentVerificationSummary {
        #   id
        #   status
        # }
      }
    }
  }
`;
