import { gql } from 'apollo-boost';

export const ALL_REPORTS_QUERY = gql`
  query AllReports(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $status: [String]
    $businessArea: String!
    $createdFrom: Date
    $createdTo: Date
    $reportType: [String]
  ) {
    allReports(
      before: $before
      after: $after
      first: $first
      last: $last
      status: $status
      businessArea: $businessArea
      createdFrom: $createdFrom
      createdTo: $createdTo
      reportType: $reportType
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      totalCount
      edgeCount
      edges {
        cursor
        node {
          id
          reportType
          dateFrom
          dateTo
          status
          createdAt
          createdBy {
            firstName
            lastName
          }
        }
      }
    }
  }
`;
