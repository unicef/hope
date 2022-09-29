import { gql } from 'apollo-boost';

export const DISCARD_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation DiscardPaymentVerificationPlan($paymentVerificationPlanId: ID!) {
    discardPaymentVerificationPlan(
      paymentVerificationPlanId: $paymentVerificationPlanId
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
        #       sampleSize
        #       receivedCount
        #       notReceivedCount
        #       respondedCount
        #       receivedCount
        #       receivedWithProblemsCount
        #       activationDate
        #     }
        #   }
        # }
      }
    }
  }
`;
