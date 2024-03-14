import { gql } from '@apollo/client';

export const IndividualChoiceData = gql`
  query individualChoiceData {
    flagChoices {
      name
      value
    }
    individualSearchTypesChoices {
      name
      value
    }
  }
`;
