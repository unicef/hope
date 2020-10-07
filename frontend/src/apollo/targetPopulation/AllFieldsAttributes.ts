import { gql } from 'apollo-boost';

export const AllFieldsAttributes = gql`
  query AllFieldsAttributes {
    allFieldsAttributes {
      id
      name
      labelEn
      associatedWith
      isFlexField
    }
  }
`;
