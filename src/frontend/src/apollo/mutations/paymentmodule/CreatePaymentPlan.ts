import { gql } from '@apollo/client';

export const CREATE_PAYMENT_PLAN = gql`
  mutation CreatePP(
    $programCycleId: ID!
    $name: String!
    $targetingCriteria: TargetingCriteriaObjectType!
    $excludedIds: String!
    $exclusionReason: String
  ) {
    createPaymentPlan(
      input: {
        programCycleId: $programCycleId
        name: $name
        targetingCriteria: $targetingCriteria
        excludedIds: $excludedIds
        exclusionReason: $exclusionReason
      }
    ) {
      paymentPlan {
        id
      }
    }
  }
`;
