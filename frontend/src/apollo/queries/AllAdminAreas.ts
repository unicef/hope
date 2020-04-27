import { gql } from 'apollo-boost';

export const ALL_ADMIN_AREAS_QUERY = gql`
  query AllAdminAreas($title: String, $businessArea: String, $first: Int) {
    allAdminAreas(
      title_Icontains: $title
      businessArea: $businessArea
      first: $first
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
          title
        }
      }
    }
  }
`;
