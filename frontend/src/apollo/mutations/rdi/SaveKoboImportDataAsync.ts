import { gql } from '@apollo/client';

export const SAVE_KOBO_IMPORT_DATA_ASYNC = gql`
  mutation SaveKoboImportDataAsync(
    $businessAreaSlug: String!
    $koboAssetId: Upload!
    $onlyActiveSubmissions: Boolean!
  ) {
    saveKoboImportDataAsync(
      businessAreaSlug: $businessAreaSlug
      uid: $koboAssetId
      onlyActiveSubmissions: $onlyActiveSubmissions
    ) {
      importData {
        id
        status
      }
    }
  }
`;
