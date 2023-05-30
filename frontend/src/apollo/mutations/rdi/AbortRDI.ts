import { gql } from 'apollo-boost';

export const ABORT_RDI = gql`
  mutation AbortRDI($id: ID!) {
    abortRegistrationDataImport(id: $id) {
      registrationDataImport {
        id
        status
      }
    }
  }
`;
