import { gql } from '@apollo/client';

export const ALL_IMPORTED_HOUSEHOLDS_QUERY = gql`
  query AllImportedHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $rdiId: String
    $orderBy: String
    $businessArea: String
  ) {
    allImportedHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      rdiId: $rdiId
      orderBy: $orderBy
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
          ...importedHouseholdMinimal
        }
      }
    }
  }
`;
