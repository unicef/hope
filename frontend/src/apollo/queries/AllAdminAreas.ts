import { gql } from 'apollo-boost';

export const ALL_ADMIN_AREAS_QUERY = gql`
  query AllAdminAreas(
    $title: String
    $businessArea: String
    $level: Int
    $first: Int
  ) {
    allAdminAreas(
      title_Istartswith: $title
      businessArea: $businessArea
      first: $first
      level: $level
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
