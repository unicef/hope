import { gql } from '@apollo/client';

export const ImportedIndividualFields = gql`
  query ImportedIndividualFields($businessAreaSlug: String) {
    allFieldsAttributes(businessAreaSlug: $businessAreaSlug) {
      isFlexField
      id
      type
      name
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
