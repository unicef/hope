import { gql } from '@apollo/client';

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
