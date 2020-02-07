import { gql } from 'apollo-boost';

export const AllHouseholds = gql`
query AllHouseholds(
    $after: String
    $before: String
    $count: Int
    $orderBy: String) {
        allHouseholds(
            after: $after
            before: $before
            first: $count
          ) {
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
              }
              totalCount
          }
}`