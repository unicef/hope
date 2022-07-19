import { gql } from 'apollo-boost';

export const RESTART_CREATE_REPORT_MUTATION = gql`
  mutation RestartCreateReport($reportData: RestartCreateReportInput!) {
    restartCreateReport(reportData: $reportData) {
      report {
        id
        status
        reportType
        createdAt
        dateFrom
        dateTo
        fileUrl
        createdBy {
          firstName
          lastName
        }
        adminArea {
          edges {
            node {
              name
            }
          }
        }
        program {
          name
        }
      }
    }
  }
`;
