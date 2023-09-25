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
    $totalDeliveredQuantityUsdFrom: Float
    $totalDeliveredQuantityUsdTo: Float
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
      totalDeliveredQuantityUsdFrom: $totalDeliveredQuantityUsdFrom
      totalDeliveredQuantityUsdTo: $totalDeliveredQuantityUsdTo
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
          unicefId
          name
          status
          totalEntitledQuantityUsd
          totalUndeliveredQuantityUsd
          totalUndeliveredQuantityUsd
          startDate
          endDate
        }
      }
    }
  }
`;
