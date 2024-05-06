import { gql } from '@apollo/client';

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
