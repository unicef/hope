import { gql } from 'apollo-boost';

export const ALL_USERS_QUERY = gql`
  query AllUsers(
    $fullName: String
    $first: Int
    $last: Int
    $after: String
    $before: String
    $orderBy: String
  ) {
    allUsers(
      fullName: $fullName
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
          username
          email
          isActive
          lastlogin
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
