import { gql } from 'apollo-boost';

export const USERS_FILTER_QUERY = gql`
  query AllUsersForFilters(
    $businessArea: String!
    $first: Int
    $last: Int
    $after: String
    $before: String
    $orderBy: String
    $search: String
  ) {
    allUsers(
      businessArea: $businessArea
      first: $first
      last: $last
      after: $after
      before: $before
      orderBy: $orderBy
      search: $search
    ) {
      edges {
        node {
          id
          firstName
          lastName
          email
        }
      }
    }
  }
`;
