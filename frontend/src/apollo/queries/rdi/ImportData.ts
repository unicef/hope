import { gql } from 'apollo-boost';

export const IMPORT_DATA_QUERY = gql`
  query ImportData($id: ID!) {
    importData(id: $id) {
      id
      status
      numberOfIndividuals
      numberOfHouseholds
      error
      validationErrors {
        header
        message
      }
    }
  }
`;
