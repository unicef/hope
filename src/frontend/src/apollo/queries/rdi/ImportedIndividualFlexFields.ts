import { gql } from '@apollo/client';

export const IMPORTED_INDIVIDUAL_FLEX_FIELDS_QUERY = gql`
  query ImportedIndividualFlexFields($id: ID!) {
    importedIndividual(id: $id) {
      id
      flexFields
    }
  }
`;
