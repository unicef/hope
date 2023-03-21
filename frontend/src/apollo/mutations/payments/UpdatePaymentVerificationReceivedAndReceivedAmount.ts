import { gql } from 'apollo-boost';

export const UPDATE_PAYMENT_VERIFICATION_STATUS_AND_RECEIVED_AMOUNT = gql`
  mutation updatePaymentVerificationReceivedAndReceivedAmount(
    $paymentVerificationId: ID!
    $receivedAmount: Decimal!
    $received: Boolean!
  ) {
    updatePaymentVerificationReceivedAndReceivedAmount(
      paymentVerificationId: $paymentVerificationId
      receivedAmount: $receivedAmount
      received: $received
    ) {
      paymentVerification {
        id
        status
        receivedAmount
        paymentVerificationPlan {
          id
          receivedCount
          notReceivedCount
          respondedCount
          receivedCount
          receivedWithProblemsCount
        }
      }
    }
  }
`;
