import { gql } from '@apollo/client';

export const SAVE_KOBO_IMPORT_DATA = gql`
  mutation SaveKoboImportData(
    $businessAreaSlug: String!
    $projectId: Upload!
    $onlyActiveSubmissions: Boolean!
  ) {
    saveKoboImportDataAsync(
      businessAreaSlug: $businessAreaSlug
      uid: $projectId
      onlyActiveSubmissions: $onlyActiveSubmissions
    ) {
      importData {
        id
      }
    }
  }
`;
