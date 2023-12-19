import { gql } from 'apollo-boost';

export const DataCollectionTypeChoiceData = gql`
  query dataCollectionTypeChoiceData {
    dataCollectionTypeChoices {
      name
      value
      description
    }
  }
`;
