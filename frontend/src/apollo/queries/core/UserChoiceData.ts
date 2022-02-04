import { gql } from 'apollo-boost';

export const UserChoiceData = gql`
  query userChoiceData {
    userRolesChoices {
      name
      value
    }
    userStatusChoices {
      name
      value
    }
    userPartnerChoices {
      name
      value
    }
  }
`;
