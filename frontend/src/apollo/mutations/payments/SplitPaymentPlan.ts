import { gql } from "apollo-boost";

export const SPLIT_PAYMENT_PLAN = gql`
  mutation SplitPP(
    $paymentPlanId: ID!
    $splitType: String!
    $paymentsNo: Int!
  ) {
    splitPaymentPlan(
      paymentPlanId: $paymentPlanId
      splitType: $splitType
      paymentsNo: $paymentsNo
    ) {
      paymentPlan {
        id
      }
    }
  }
`;
