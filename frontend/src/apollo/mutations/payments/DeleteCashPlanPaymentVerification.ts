import { gql } from 'apollo-boost';

export const DELETE_CASH_PLAN_PAYMENT_VERIFICATION = gql`
  mutation DeleteCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
    deleteCashPlanPaymentVerification(
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
