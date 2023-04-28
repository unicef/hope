import { gql } from 'apollo-boost';

export const CREATE_FOLLOW_UP_PAYMENT_PLAN = gql`
  mutation CreateFollowUpPP(
    $dispersionStartDate: Date!
    $dispersionEndDate: Date!
    $paymentPlanId: ID!
  ) {
    createFollowUpPaymentPlan(
      dispersionStartDate: $dispersionStartDate
      dispersionEndDate: $dispersionEndDate
      paymentPlanId: $paymentPlanId
    ) {
      paymentPlan {
        id
        unicefId
      }
    }
  }
`;
