import { gql } from '@apollo/client';

export const OPEN_PAYMENT_PLAN = gql`
  mutation OpenPP(
    $paymentPlanId: ID!
    $dispersionStartDate: Date!
    $dispersionEndDate: Date!
    $currency: String!
  ) {
    openPaymentPlan(
      input: {
        paymentPlanId: $paymentPlanId
        dispersionStartDate: $dispersionStartDate
        dispersionEndDate: $dispersionEndDate
        currency: $currency
      }
    ) {
      paymentPlan {
        id
      }
    }
  }
`;
