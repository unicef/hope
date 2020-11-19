import { gql } from 'apollo-boost';

export const AllAddIndividualFields = gql`
  query AllAddIndividualFields {
    allAddIndividualsFieldsAttributes {
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
