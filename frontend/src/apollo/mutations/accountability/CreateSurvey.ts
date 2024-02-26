import { gql } from '@apollo/client';

export const CREATE_SURVEY_MUTATION = gql`
  mutation CreateSurveyAccountability($input: CreateSurveyInput!) {
    createSurvey(input: $input) {
      survey {
        id
      }
    }
  }
`;
