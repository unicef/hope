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
      pduData {
        id
        numberOfRounds
        roundsNames
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
