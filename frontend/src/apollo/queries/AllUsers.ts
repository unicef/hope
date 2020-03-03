import { gql } from 'apollo-boost';

export const ALL_PROGRAMS_QUERY = gql`
  query AllUsers {
    allUsers {
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
