import { gql } from '@apollo/client';

export const COPY_TARGETING_CRITERIA_MUTATION = gql`
  mutation CopyTargetingCriteria(
    $name: String!
    $paymentPlanId: ID!
    $programCycleId: ID!
  ) {
    copyTargetingCriteria(
      name: $name
      paymentPlanId: $paymentPlanId
      programCycleId: $programCycleId
    ) {
      paymentPlan {
        id
        name
      }
    }
  }
`;
