import { gql } from 'apollo-boost';

export const MARK_PAYMENT_RECORD_AS_FAILED = gql`
  mutation markPRAsFailed($paymentRecordId: ID!) {
    markPaymentRecordAsFailed(paymentRecordId: $paymentRecordId) {
      paymentRecord {
        ...paymentRecordDetails
      }
    }
  }
`;
