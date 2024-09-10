import { gql } from '@apollo/client';

export const LoggedChecker = gql`
  query LoggedChecker {
    me {
      id
    }
  }
`;
