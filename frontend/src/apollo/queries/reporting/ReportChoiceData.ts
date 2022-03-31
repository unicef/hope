import { gql } from 'apollo-boost';

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
