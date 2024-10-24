import { gql } from '@apollo/client';

export const RegistrationChoices = gql`
  query registrationChoices {
    registrationDataStatusChoices {
      name
      value
    }
  }
`;
