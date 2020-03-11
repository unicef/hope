import { gql } from 'apollo-boost';

export const ALL_IMPORTED_INDIVIDUALS_QUERY = gql`
  query AllImportedIndividuals(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $rdiId: String
  ) {
    allImportedIndividuals(
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
          ...importedIndividualMinimal
        }
      }
    }
  }
`;
