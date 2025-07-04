import { gql } from '@apollo/client';

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
    accountTypeChoices {
      name
      value
    }
    accountFinancialInstitutionChoices {
      name
      value
    }
  }
`;
