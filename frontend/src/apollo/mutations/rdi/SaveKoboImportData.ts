import { gql } from 'apollo-boost';

export const SAVE_KOBO_IMPORT_DATA = gql`
  mutation SaveKoboImportData(
    $businessAreaSlug: String!
    $projectId: Upload!
    $onlyActiveSubmissions: Boolean!
  ) {
    saveKoboImportData(
      businessAreaSlug: $businessAreaSlug
      uid: $projectId
      onlyActiveSubmissions: $onlyActiveSubmissions
    ) {
      importData {
        id
        numberOfHouseholds
        numberOfIndividuals
      }
      errors {
        header
        message
      }
    }
  }
`;
