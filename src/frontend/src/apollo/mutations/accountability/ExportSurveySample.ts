import { gql } from '@apollo/client';

export const EXPORT_SURVEY_SAMPLE_MUTATION = gql`
  mutation ExportSurveySample($surveyId: ID!) {
    exportSurveySample(surveyId: $surveyId) {
      survey {
        id
      }
    }
  }
`;
