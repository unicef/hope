import { gql } from 'apollo-boost';

export const AvailableFlows = gql`
  query SurveyAvailableFlows {
    surveyAvailableFlows {
      id
      name
    }
  }
`;
