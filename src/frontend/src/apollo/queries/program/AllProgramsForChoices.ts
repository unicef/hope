import { gql } from '@apollo/client';

export const AllProgramsForChoices = gql`
  query AllProgramsForChoices(
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
    $name: String
    $compatibleDct: Boolean
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
      name: $name
      compatibleDct: $compatibleDct
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
          dataCollectingType {
            id
            code
            type
            label
            active
            individualFiltersAvailable
            householdFiltersAvailable
            description
          }
          pduFields {
            id
          }
        }
      }
    }
  }
`;
