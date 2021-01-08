import { gql } from 'apollo-boost';

export const REPORT_QUERY = gql`
  query Report($id: ID!) {
    report(id: $id) {
      id
      status
      reportType
      createdAt
      dateFrom
      dateTo
      createdBy {
        firstName
        lastName
      }
      adminArea {
        title
      }
      program {
        name
      }
    }
  }
`;
