import { gql } from 'apollo-boost';

export const DELETE_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation DeletePaymentVerificationPlan($paymentVerificationPlanId: ID!) {
    deletePaymentVerificationPlan(
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
      }
    }
  }
`;
