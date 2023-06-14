import { gql } from 'apollo-boost';

export const ALL_ACTIVE_PROGRAMS_QUERY = gql`
  query AllActivePrograms(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $status: [String]
    $sector: [String]
    $businessArea: String!
    $search: String
    $numberOfHouseholds: String
    $budget: String
    $startDate: Date
    $endDate: Date
    $orderBy: String
  ) {
    allActivePrograms(
      before: $before
      after: $after
      first: $first
      last: $last
      status: $status
      sector: $sector
      businessArea: $businessArea
      search: $search
      numberOfHouseholds: $numberOfHouseholds
      budget: $budget
      orderBy: $orderBy
      startDate: $startDate
      endDate: $endDate
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
          name
          status
          startDate
          endDate
          sector
          totalNumberOfHouseholds
          budget
        }
      }
    }
  }
`;
