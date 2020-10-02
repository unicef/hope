import { gql } from 'apollo-boost';

export const ALL_PROGRAMS_QUERY = gql`
  query AllPrograms(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $status: [String]
    $sector: [String]
    $businessArea: String!
    $search: String
    $numberOfHouseholds: Int
    $budget: Float
    $orderBy: String
  ) {
    allPrograms(
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      status: $status
      sector: $sector
      businessArea: $businessArea
      search: $search
      numberOfHouseholds: $numberOfHouseholds
      budget: $budget
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
