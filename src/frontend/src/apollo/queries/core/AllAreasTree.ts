import { gql } from '@apollo/client';

export const ALL_AREAS_TREE_QUERY = gql`
  query AllAreasTree($businessArea: String!) {
    allAreasTree(businessArea: $businessArea) {
      id
      pCode
      name
      level
      areas {
        id
        name
        level
        pCode
        areas {
          id
          name
          pCode
          areas {
            id
            name
            pCode
          }
        }
      }
    }
  }
`;
