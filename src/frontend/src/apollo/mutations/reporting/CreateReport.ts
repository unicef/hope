import { gql } from '@apollo/client';

export const CREATE_REPORT_MUTATION = gql`
  mutation CreateReport($reportData: CreateReportInput!) {
    createReport(reportData: $reportData) {
      report {
        id
      }
    }
  }
`;
