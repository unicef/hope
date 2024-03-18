import { gql } from '@apollo/client';

export const ALL_AREAS_TREE_QUERY = gql`
  query AllAreasTree($businessArea: String!) {
    allAreasTree(businessArea: $businessArea) {
      id
      name
      pCode
      level
      areas {
        id
        name
        pCode
        level
        areas {
          id
          name
          pCode
          level
          areas {
            id
            name
            pCode
            level
          }
        }
      }
    }
  }
`;
