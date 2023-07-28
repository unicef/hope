import { gql } from 'apollo-boost';

export const ALL_MERGED_HOUSEHOLDS_QUERY = gql`
  query AllMergedHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $rdiId: String
    $orderBy: String
    $businessArea: String
  ) {
    allMergedHouseholds(
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
          ...mergedHouseholdMinimal
        }
      }
    }
  }
`;
