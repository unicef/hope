import { gql } from '@apollo/client';

export const IndividualFields = gql`
  query IndividualFields($businessAreaSlug: String, $programId: String) {
    allFieldsAttributes(
      businessAreaSlug: $businessAreaSlug
      programId: $programId
    ) {
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
      pduData {
        id
        subtype
        numberOfRounds
        roundsNames
      }
    }
  }
`;
