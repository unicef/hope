import { gql } from '@apollo/client';

export const Me = gql`
  query Me {
    me {
      id
      username
      email
      firstName
      lastName
      permissionsInScope
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
