import { gql } from '@apollo/client';

export const AllProgramsForTable = gql`
  query AllProgramsForTable(
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
    $dataCollectingType: String
  ) {
    allPrograms(
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
      dataCollectingType: $dataCollectingType
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
          startDate
          endDate
          status
          budget
          sector
          totalNumberOfHouseholds
        }
      }
    }
  }
`;
