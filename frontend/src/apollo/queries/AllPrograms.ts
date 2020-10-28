import { gql } from 'apollo-boost';

export const ALL_PROGRAMS_QUERY = gql`
  query AllPrograms(
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
          caId
          description
          budget
          frequencyOfPayments
          populationGoal
          sector
          totalNumberOfHouseholds
          individualDataNeeded
        }
      }
    }
  }
`;
