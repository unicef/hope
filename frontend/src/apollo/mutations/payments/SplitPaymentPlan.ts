import { gql } from "apollo-boost";

export const SPLIT_PAYMENT_PLAN = gql`
  mutation SplitPP(
    $paymentPlanId: ID!
    $splitType: String!
    $paymentParts: Int!
  ) {
    splitPaymentPlan(
      paymentPlanId: $paymentPlanId
      splitType: $splitType
      paymentParts: $paymentParts
    ) {
      paymentPlan {
        id
      }
    }
  }
`;
