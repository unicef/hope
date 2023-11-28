import { gql } from 'apollo-boost';

export const UserPartnerChoices = gql`
  query UserPartnerChoices {
    userPartnerChoices {
      name
      value
    }
  }
`;
