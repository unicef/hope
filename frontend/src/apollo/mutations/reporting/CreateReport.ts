import { gql } from '@apollo/client';

export const CREATE_REPORT_MUTATION = gql`
  mutation CreateReport($reportData: CreateReportInput!) {
    createReport(reportData: $reportData) {
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
