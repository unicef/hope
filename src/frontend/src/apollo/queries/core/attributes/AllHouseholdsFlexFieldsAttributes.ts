import { gql } from '@apollo/client';

export const AllHouseholdsFlexFieldsAttributes = gql`
  query AllHouseholdsFlexFieldsAttributes {
    allHouseholdsFlexFieldsAttributes {
      isFlexField
      id
      type
      name
      required
      associatedWith
      labels {
        language
        label
      }
      labelEn
      hint
      choices {
        labels {
          label
          language
        }
        labelEn
        value
        admin
        listName
      }
    }
  }
`;
