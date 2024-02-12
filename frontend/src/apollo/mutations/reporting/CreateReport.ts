import { gql } from 'apollo-boost';

export const CREATE_REPORT_MUTATION = gql`
  mutation CreateReport($reportData: CreateReportInput!) {
    createReport(reportData: $reportData) {
      report {
        id
      }
    }
  }
`;
