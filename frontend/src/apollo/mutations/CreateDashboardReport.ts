import { gql } from 'apollo-boost';

export const CREATE_DASHBOARD_REPORT_MUTATION = gql`
  mutation CreateDashboardReport($reportData: CreateDashboardReportInput!) {
    createDashboardReport(reportData: $reportData) {
      success
    }
  }
`;
