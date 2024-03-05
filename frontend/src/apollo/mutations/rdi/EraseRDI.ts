import { gql } from '@apollo/client';

export const ERASE_RDI = gql`
  mutation eraseRDI($id: ID!) {
    eraseRegistrationDataImport(id: $id) {
      registrationDataImport {
        id
        status
        erased
      }
    }
  }
`;
