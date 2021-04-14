import { gql } from 'apollo-boost';

export const UPDATE_PAYMENT_VERIFICATION_STATUS_AND_RECEIVED_AMOUNT = gql`
  mutation updatePaymentVerificationStatusAndReceivedAmount(
    $paymentVerificationId: ID!
    $receivedAmount: Decimal!
    $status: PaymentVerificationStatusForUpdate
  ) {
    updatePaymentVerificationStatusAndReceivedAmount(
      paymentVerificationId: $paymentVerificationId
      receivedAmount: $receivedAmount
      status: $status
    ) {
      paymentVerification {
        id
        status
        receivedAmount
      }
    }
  }
`;
