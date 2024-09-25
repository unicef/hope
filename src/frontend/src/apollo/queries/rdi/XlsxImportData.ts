import { gql } from '@apollo/client';

export const IMPORT_DATA_QUERY = gql`
  query XlsxImportData($id: ID!) {
    importData(id: $id) {
      id
      status
      numberOfIndividuals
      numberOfHouseholds
      error
      xlsxValidationErrors {
        rowNumber
        header
        message
      }
    }
  }
`;
