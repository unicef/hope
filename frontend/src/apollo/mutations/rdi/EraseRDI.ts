import { gql } from 'apollo-boost';

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
