import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_VERIFICATION_QUERY = gql`
  query PaymentRecordVerification($id: ID!) {
    paymentRecordVerification(id: $id) {
      id
      status
      statusDate
      receivedAmount
      isManuallyEditable
    }
  }
`;
