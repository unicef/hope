import { gql } from 'apollo-boost';

export const REVERT_MARK_PAYMENT_RECORD_AS_FAILED = gql`
  mutation revertMarkPRAsFailed(
    $paymentRecordId: ID!
    $deliveredQuantity: Decimal!
    $deliveryDate: Date!
  ) {
    revertMarkPaymentRecordAsFailed(
      paymentRecordId: $paymentRecordId
      deliveredQuantity: $deliveredQuantity
      deliveryDate: $deliveryDate
    ) {
      paymentRecord {
        ...paymentRecordDetails
      }
    }
  }
`;
