import { gql } from 'apollo-boost';

export const REFUSE_RDI = gql`
  mutation RefuseRDI($id: ID!) {
    refuseRegistrationDataImport(id: $id) {
      registrationDataImport {
        id
        status
      }
    }
  }
`;
