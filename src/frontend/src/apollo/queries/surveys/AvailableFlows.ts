import { gql } from '@apollo/client';

export const AvailableFlows = gql`
  query SurveyAvailableFlows {
    surveyAvailableFlows {
      id
      name
    }
  }
`;
