import { gql } from '@apollo/client';

export const MARK_PAYMENT_RECORD_AS_FAILED = gql`
  mutation markPRAsFailed($paymentRecordId: ID!) {
    markPaymentRecordAsFailed(paymentRecordId: $paymentRecordId) {
      paymentRecord {
        ...paymentRecordDetails
      }
    }
  }
`;
