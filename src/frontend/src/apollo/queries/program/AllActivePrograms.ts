import { gql } from '@apollo/client';

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
    $budget: String
    $startDate: Date
    $endDate: Date
    $orderBy: String
    $numberOfHouseholdsWithTpInProgram: String
    $dataCollectingType: String
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
      budget: $budget
      orderBy: $orderBy
      startDate: $startDate
      endDate: $endDate
      numberOfHouseholdsWithTpInProgram: $numberOfHouseholdsWithTpInProgram
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
          status
          startDate
          endDate
          sector
          totalNumberOfHouseholds
          totalNumberOfHouseholdsWithTpInProgram
          budget
        }
      }
    }
  }
`;
