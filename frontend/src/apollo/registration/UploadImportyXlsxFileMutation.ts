import { gql } from 'apollo-boost';

export const UPLOAD_IMPORT_XSLSX_MUTATION = gql`
  mutation UploadImportDataXlsxFile($file: Upload!) {
    uploadImportDataXlsxFile(file: $file) {
      importData {
        id
        numberOfIndividuals
        numberOfHouseholds
        registrationDataImport {
          edges {
            node {
              id
            }
          }
        }
      }
    }
  }
`;
