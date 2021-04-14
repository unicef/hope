import { gql } from 'apollo-boost';

export const ALL_IMPORTED_HOUSEHOLDS_QUERY = gql`
  query AllKoboProjects(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $businessAreaSlug: String!
  ) {
    allKoboProjects(
      after: $after
      before: $before
      first: $first
      last: $last
      businessAreaSlug: $businessAreaSlug
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
          name
          id
        }
      }
    }
  }
`;
