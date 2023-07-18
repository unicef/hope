import { gql } from 'apollo-boost';

export const REFUSE_RDI = gql`
  mutation RefuseRDI($id: ID!, $refuseReason: String) {
    refuseRegistrationDataImport(id: $id, refuseReason: $refuseReason) {
      registrationDataImport {
        id
        status
        refuseReason
      }
    }
  }
`;
