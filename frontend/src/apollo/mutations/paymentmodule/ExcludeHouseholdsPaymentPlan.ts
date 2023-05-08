import { gql } from 'apollo-boost';

export const EXCLUDE_HOUSEHOLDS_PP = gql`
  mutation ExcludeHouseholdsPP(
    $paymentPlanId: ID!
    $excludedHouseholdsIds: [String]!
  ) {
    excludeHouseholds(
      paymentPlanId: $paymentPlanId
      excludedHouseholdsIds: $excludedHouseholdsIds
    ) {
      paymentPlan {
        id
        excludedHouseholds {
          id
          unicefId
        }
      }
    }
  }
`;
