import { gql } from '@apollo/client';

export const ALL_ADMIN_AREAS_QUERY = gql`
  query AllAdminAreas(
    $name: String
    $businessArea: String
    $level: Int
    $first: Int
    $parentId: String
  ) {
    allAdminAreas(
      name_Istartswith: $name
      businessArea: $businessArea
      first: $first
      level: $level
      parentId: $parentId
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
          name
          pCode
        }
      }
    }
  }
`;
