import { gql } from 'apollo-boost';

export const EXCLUDE_HOUSEHOLDS_PP = gql`
  mutation ExcludeHouseholdsPP(
    $paymentPlanId: ID!
    $excludedHouseholdsIds: [String]!
    $exclusionReason: String
  ) {
    excludeHouseholds(
      paymentPlanId: $paymentPlanId
      excludedHouseholdsIds: $excludedHouseholdsIds
      exclusionReason: $exclusionReason
    ) {
      paymentPlan {
        id
        status
        backgroundActionStatus
        excludeHouseholdError
        exclusionReason
        excludedHouseholds {
          id
          unicefId
        }
      }
    }
  }
`;
