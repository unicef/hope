import { gql } from '@apollo/client';

export const AllIndividualsFlexFieldsAttributes = gql`
  query AllIndividualsFlexFieldsAttributes {
    allIndividualsFlexFieldsAttributes {
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
