import { gql } from 'apollo-boost';

export const FINISH_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation FinishPaymentVerificationPlan($cashPlanVerificationId: ID!) {
    finishPaymentVerificationPlan(
      paymentVerificationPlanId: $cashPlanVerificationId
    ) {
      cashPlan {
        id
        status
        statusDate
        verificationPlans {
          edges {
            node {
              id
              status
              completionDate
            }
          }
        }
        paymentVerificationSummary {
          id
          status
        }
      }
    }
  }
`;
