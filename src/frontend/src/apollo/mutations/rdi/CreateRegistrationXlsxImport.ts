import { gql } from '@apollo/client';

export const CREATE_REGISTRATION_DATA_IMPORT_QUERY = gql`
  mutation CreateRegistrationXlsxImport(
    $registrationDataImportData: RegistrationXlsxImportMutationInput!
  ) {
    registrationXlsxImport(
      registrationDataImportData: $registrationDataImportData
    ) {
      registrationDataImport {
        id
        name
        dataSource
        screenBeneficiary
      }
      validationErrors
    }
  }
`;
