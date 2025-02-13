import { gql } from '@apollo/client';

export const CREATE_REGISTRATION_PROGRAM_POPULATION_IMPORT_MUTATION = gql`
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
        screenBeneficiary
      }
      validationErrors
    }
  }
`;
