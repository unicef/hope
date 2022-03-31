import { gql } from 'apollo-boost';

export const USERS_FILTER_QUERY = gql`
  query AllUsersForFilters(
    $businessArea: String!
    $first: Int
    $last: Int
    $after: String
    $before: String
    $orderBy: String
  ) {
    allUsers(
      businessArea: $businessArea
      first: $first
      last: $last
      after: $after
      before: $before
      orderBy: $orderBy
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          email
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
