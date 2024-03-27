import { gql } from '@apollo/client';

export const UserChoiceData = gql`
  query userChoiceData {
    userRolesChoices {
      name
      value
      subsystem
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
