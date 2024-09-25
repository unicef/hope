import { gql } from '@apollo/client';

export const CREATE_REGISTRATION_DATA_IMPORT_MUTATION = gql`
  mutation CreateRegistrationProgramPopulationImport(
    $registrationDataImportData: RegistrationProgramPopulationImportMutationInput!
  ) {
    registrationProgramPopulationImport(
      registrationDataImportData: $registrationDataImportData
    ) {
      registrationDataImport {
        id
        name
        dataSource
        datahubId
        screenBeneficiary
      }
      validationErrors
    }
  }
`;
