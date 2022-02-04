import { gql } from 'apollo-boost';

export const AllEditHouseholdFields = gql`
  query AllEditHouseholdFields {
    allEditHouseholdFieldsAttributes {
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
    countriesChoices {
      name
      value
    }
  }
`;
