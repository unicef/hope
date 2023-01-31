import { gql } from 'apollo-boost';

export const REVERT_MARK_PAYMENT_RECORD_AS_FAILED = gql`
  mutation revertMarkPRAsFailed($paymentRecordId: ID!) {
    revertMarkPaymentRecordAsFailed(paymentRecordId: $paymentRecordId) {
      paymentRecord {
        ...paymentRecordDetails
      }
    }
  }
`;
