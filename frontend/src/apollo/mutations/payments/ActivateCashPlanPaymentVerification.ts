import { gql } from 'apollo-boost';

export const ACTIVATE_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation ActivatePaymentVerificationPlan($paymentVerificationPlanId: ID!) {
    activatePaymentVerificationPlan(
      paymentVerificationPlanId: $paymentVerificationPlanId
    ) {
      paymentPlan {
        id
        # status
        # statusDate
        verificationPlans {
          edges {
            node {
              id
              status
              activationDate
            }
          }
        }
        paymentVerificationSummary {
          id
          status
        }
      }
      validationErrors
    }
  }
`;
