import { gql } from 'apollo-boost';

export const APPROVE_REGISTRATION_DATA_IMPORT_MUTATION = gql`
  mutation ApproveRDI($id: ID!) {
    approveRegistrationDataImport(id: $id) {
      registrationDataImport {
        ...registrationDetailed
      }
    }
  }
`;
