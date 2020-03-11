import { gql } from 'apollo-boost';

export const ALL_IMPORTED_HOUSEHOLDS_QUERY = gql`
  query AllImportedHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $rdiId: String
  ) {
    allImportedHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      rdiId: $rdiId
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edges {
        cursor
        node {
          ...importedHouseholdMinimal
        }
      }
    }
  }
`;
