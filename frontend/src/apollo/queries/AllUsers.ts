import { gql } from 'apollo-boost';

export const ALL_PROGRAMS_QUERY = gql`
  query AllUsers($fullName: String, $first: Int) {
    allUsers(fullName: $fullName, first: $first) {
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
        }
      }
    }
  }
`;
