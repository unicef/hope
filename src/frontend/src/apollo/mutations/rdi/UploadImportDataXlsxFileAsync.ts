import { gql } from '@apollo/client';

export const UPLOAD_IMPORT_XSLSX_MUTATION_ASYNC = gql`
  mutation UploadImportDataXlsxFileAsync(
    $file: Upload!
    $businessAreaSlug: String!
  ) {
    uploadImportDataXlsxFileAsync(
      file: $file
      businessAreaSlug: $businessAreaSlug
    ) {
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
