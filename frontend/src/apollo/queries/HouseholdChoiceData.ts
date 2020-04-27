import { gql } from 'apollo-boost';

export const HouseholdChoiceData = gql`
  query householdChoiceData {
    residenceStatusChoices {
      name
      value
    }
    relationshipChoices {
      name
      value
    }
    roleChoices {
      name
      value
    }
  }
`;
