import { gql } from 'apollo-boost';

export const LoggedChecker = gql`
  query LoggedChecker {
    me {
      id
    }
  }
`;
