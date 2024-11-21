import { gql } from '@apollo/client';

export const AllCollectorFieldsAttributes = gql`
  query AllCollectorFieldsAttributes {
    allCollectorFieldsAttributes {
      id
      name
      labelEn
      associatedWith
      isFlexField
      type
      choices {
        labelEn
        value
        admin
        listName
      }
    }
  }
`;
