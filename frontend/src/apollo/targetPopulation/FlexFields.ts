import { gql } from 'apollo-boost';

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
