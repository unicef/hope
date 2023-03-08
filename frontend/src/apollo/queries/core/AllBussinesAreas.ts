import { gql } from 'apollo-boost';

export const ALL_BUSINESS_AREAS_QUERY = gql`
  query AllBusinessAreas($slug: String) {
    allBusinessAreas(slug: $slug) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      edges {
        node {
          id
          name
          slug
        }
      }
    }
  }
`;
