import { gql } from 'apollo-boost';

export const UPLOAD_IMPORT_XSLSX_MUTATION = gql`
  mutation UploadImportDataXlsxFile($file: Upload!, $businessAreaSlug: String!) {
    uploadImportDataXlsxFile(file: $file, businessAreaSlug: $businessAreaSlug) {
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
