import { gql } from '@apollo/client';

export const AllEditPeopleFieldsAttributes = gql`
  query AllEditPeopleFields {
    allEditPeopleFieldsAttributes {
      id
      type
      name
      required
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
      isFlexField
    }
    countriesChoices {
      name
      value
    }
    documentTypeChoices {
      name
      value
    }
    identityTypeChoices {
      name
      value
    }
  }
`;
