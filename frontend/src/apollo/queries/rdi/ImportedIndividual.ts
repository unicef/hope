import { gql } from 'apollo-boost';

export const IMPORTED_INDIVIDUAL_QUERY = gql`
  query ImportedIndividual($id: ID!) {
    importedIndividual(id: $id) {
      ...importedIndividualDetailed
    }
  }
`;
