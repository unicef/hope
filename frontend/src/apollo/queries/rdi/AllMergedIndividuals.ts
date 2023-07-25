import { gql } from 'apollo-boost';

export const ALL_MERGED_INDIVIDUALS_QUERY = gql`
  query AllMergedIndividuals(
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
    allMergedIndividuals(
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
          ...mergedIndividualMinimal
        }
      }
    }
  }
`;
