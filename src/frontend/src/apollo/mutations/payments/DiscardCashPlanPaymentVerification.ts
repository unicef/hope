import { gql } from '@apollo/client';

export const DISCARD_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation DiscardPaymentVerificationPlan($paymentVerificationPlanId: ID!) {
    discardPaymentVerificationPlan(
      paymentVerificationPlanId: $paymentVerificationPlanId
    ) {
      paymentPlan {
        id
        verificationPlans {
          totalCount
          edges {
            node {
              id
              status
              sampleSize
              receivedCount
              notReceivedCount
              respondedCount
              receivedCount
              receivedWithProblemsCount
              activationDate
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
