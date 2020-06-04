import { gql } from 'apollo-boost';

export const CREATE_REGISTRATION_DATA_KOBO_IMPORT_QUERY = gql`
  mutation CreateRegistrationKoboImport(
    $registrationDataImportData: RegistrationKoboImportMutationInput!
  ) {
    registrationKoboImport(
      registrationDataImportData: $registrationDataImportData
    ) {
      registrationDataImport {
        id
        name
        dataSource
        datahubId
      }
    }
  }
`;
