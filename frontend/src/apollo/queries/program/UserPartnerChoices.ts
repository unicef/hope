import { gql } from '@apollo/client';

export const UserPartnerChoices = gql`
  query UserPartnerChoices {
    userPartnerChoices {
      name
      value
    }
  }
`;
