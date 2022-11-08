import { gql } from 'apollo-boost';

export const SurveysChoiceData = gql`
  query SurveysChoiceData {
    surveyCategoryChoices {
      name
      value
    }
  }
`;
