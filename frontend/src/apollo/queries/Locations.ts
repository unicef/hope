import { gql } from 'apollo-boost';

export const allLocations = gql`
  query allLocations {
    allLocations {
      edges {
        node {
          id
        }
      }
    }
  }
`;
