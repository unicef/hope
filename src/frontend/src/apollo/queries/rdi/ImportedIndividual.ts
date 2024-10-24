import { gql } from '@apollo/client';

export const IMPORTED_INDIVIDUAL_QUERY = gql`
  query ImportedIndividual($id: ID!) {
    importedIndividual(id: $id) {
      ...importedIndividualDetailed
    }
  }
`;
