import { gql } from 'apollo-boost';

export const ALL_REPORTS_QUERY = gql`
  query AllReports(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $status: [String]
    $businessArea: String!
    $createdFrom: DateTime
    $createdTo: DateTime
    $reportType: [String]
    $createdBy: ID
    $orderBy: String
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
      createdBy: $createdBy
      orderBy: $orderBy
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
          updatedAt
          createdBy {
            firstName
            lastName
          }
          fileUrl
          numberOfRecords
        }
      }
    }
  }
`;
