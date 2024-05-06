import { gql } from '@apollo/client';

export const SurveysChoiceData = gql`
  query SurveysChoiceData {
    surveyCategoryChoices {
      name
      value
    }
  }
`;
