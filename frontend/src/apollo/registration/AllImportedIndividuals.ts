import { gql } from 'apollo-boost';

export const ALL_IMPORTED_INDIVIDUALS_QUERY = gql`
  query AllImportedIndividuals(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $rdiId: String
    $household: ID
    $orderBy: String
    $duplicatesOnly: Boolean
    $businessArea: String
  ) {
    allImportedIndividuals(
      after: $after
      before: $before
      first: $first
      last: $last
      rdiId: $rdiId
      household: $household
      orderBy: $orderBy
      duplicatesOnly: $duplicatesOnly
      businessArea: $businessArea
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
