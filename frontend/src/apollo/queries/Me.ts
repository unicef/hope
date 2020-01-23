import { gql } from 'apollo-boost';

export const Me = gql`
  query Me {
    me {
      id
      username
      email
      firstName
      lastName
    }
  }
`;
