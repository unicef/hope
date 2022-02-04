import { gql } from 'apollo-boost';

export const IndividualChoiceData = gql`
  query individualChoiceData {
    flagChoices {
      name
      value
    }
  }
`;
