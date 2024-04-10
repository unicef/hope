import { gql } from '@apollo/client';

export const REPORT_QUERY = gql`
  query Report($id: ID!) {
    report(id: $id) {
      id
      status
      reportType
      createdAt
      updatedAt
      dateFrom
      dateTo
      fileUrl
      numberOfRecords
      createdBy {
        firstName
        lastName
      }
      adminArea2 {
        edges {
          node {
            name
          }
        }
      }
      adminArea1 {
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
`;
