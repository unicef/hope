import { gql } from 'apollo-boost';

export const EXCLUDE_HOUSEHOLDS_PP = gql`
  mutation ExcludeHouseholdsPP($input: //TODO!!!) {
    excludeHouseholds(input: $input) {
      paymentPlan {
        id
        excludedHouseholdsIds
    }
  }
`;
