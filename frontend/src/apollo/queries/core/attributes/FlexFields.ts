import { gql } from '@apollo/client';

export const FlexFields = gql`
  query FlexFields {
    allGroupsWithFields {
      name
      labelEn
      flexAttributes {
        id
        labelEn
        associatedWith
      }
    }
  }
`;
