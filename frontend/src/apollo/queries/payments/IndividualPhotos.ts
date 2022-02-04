import { gql } from 'apollo-boost';

export const INDIVIDUAL_PHOTOS_QUERY = gql`
  query IndividualPhotos($id: ID!) {
    individual(id: $id) {
      id
      photo
      documents {
        edges {
          node {
            id
            documentNumber
            photo
          }
        }
      }
    }
  }
`;

export const IMPORTED_INDIVIDUAL_PHOTOS_QUERY = gql`
  query ImportedIndividualPhotos($id: ID!) {
    importedIndividual(id: $id) {
      id
      photo
      documents {
        edges {
          node {
            id
            photo
          }
        }
      }
    }
  }
`;
