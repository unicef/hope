import { gql } from 'apollo-boost';

export const ImportedIndividualFields = gql`
  query ImportedIndividualFields {
    allFieldsAttributes {
      isFlexField
      id
      type
      name
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
