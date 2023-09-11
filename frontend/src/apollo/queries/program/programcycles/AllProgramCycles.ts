import { gql } from 'apollo-boost';

export const ALL_PROGRAM_CYCLES_QUERY = gql`
  query AllProgramCycles(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $search: String
    $status: [String]
    $startDate: Date
    $endDate: Date
    $orderBy: String
  ) {
    allProgramCycles(
      before: $before
      after: $after
      first: $first
      last: $last
      search: $search
      status: $status
      startDate: $startDate
      endDate: $endDate
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
          unicefId
          name
          status
          totalEntitledQuantity
          totalUndeliveredQuantity
          totalUndeliveredQuantity
          startDate
          endDate
        }
      }
    }
  }
`;
