import { gql } from '@apollo/client';

export const Me = gql`
  query Me {
    me {
      id
      username
      email
      firstName
      lastName
      isSuperuser
      businessAreas {
        edges {
          node {
            id
            name
            slug
            permissions
          }
        }
      }
    }
  }
`;
