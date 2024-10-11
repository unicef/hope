import { gql } from '@apollo/client';

export const ReportChoiceData = gql`
  query ReportChoiceData {
    reportStatusChoices {
      name
      value
    }
    reportTypesChoices {
      name
      value
    }
  }
`;
