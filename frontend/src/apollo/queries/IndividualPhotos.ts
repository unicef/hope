import {gql} from 'apollo-boost';

export const INDIVIDUAL_PHOTOS_QUERY = gql`
  query IndividualPhotos($id: ID!) {
    individual(id: $id) {
      id
      photo
      documents{
        edges{
          node{
            id
            photo
          }
        }
      }
    }
  }
`;
