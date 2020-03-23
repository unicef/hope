import { gql } from 'apollo-boost';

export const UNAPPROVE_REGISTRATION_DATA_IMPORT_MUTATION = gql`
  mutation UnapproveRDI($id: ID!) {
    unapproveRegistrationDataImport(id: $id) {
      registrationDataImport {
        ...registrationDetailed
      }
    }
  }
`;
