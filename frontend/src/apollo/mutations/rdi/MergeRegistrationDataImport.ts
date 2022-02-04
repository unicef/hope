import { gql } from 'apollo-boost';

export const MERGE_REGISTRATION_DATA_IMPORT_MUTATION = gql`
  mutation MergeRDI($id: ID!) {
    mergeRegistrationDataImport(id: $id) {
      registrationDataImport {
        ...registrationDetailed
      }
    }
  }
`;
