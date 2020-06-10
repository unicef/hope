import { gql } from 'apollo-boost';

export const SAVE_KOBO_IMPORT_DATA = gql`
  mutation SaveKoboImportData($businessAreaSlug: String!, $projectId: Upload!) {
    saveKoboImportData(businessAreaSlug: $businessAreaSlug, uid: $projectId) {
      importData {
        id
        numberOfHouseholds
        numberOfIndividuals
      }
      errors{
        header
        message
      }
    }
  }
`;
