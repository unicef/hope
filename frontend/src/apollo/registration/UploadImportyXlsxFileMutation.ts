import { gql } from 'apollo-boost';

export const UPLOAD_IMPORT_XSLSX_MUTATION = gql`
  mutation UploadImportDataXlsxFile($file: Upload!, ) {
    uploadImportDataXlsxFile(file: $file) {
      errors {
        header
        message
        rowNumber
      }
      importData {
        id
        numberOfIndividuals
        numberOfHouseholds
        registrationDataImport {
          id
        }
      }
    }
  }
`;
