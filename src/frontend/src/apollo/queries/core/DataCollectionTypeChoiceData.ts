import { gql } from '@apollo/client';

export const DataCollectionTypeChoiceData = gql`
  query dataCollectionTypeChoiceData {
    dataCollectionTypeChoices {
      name
      value
      description
      type
    }
  }
`;
