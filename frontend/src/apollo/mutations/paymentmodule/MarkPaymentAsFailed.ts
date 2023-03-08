import { gql } from 'apollo-boost';

export const MARK_PAYMENT_AS_FAILED = gql`
  mutation markPaymentAsFailed($paymentId: ID!) {
    markPaymentAsFailed(paymentId: $paymentId) {
      payment(id: $paymentId) {
        id
        unicefId
        status
        statusDate
        deliveredQuantity
        deliveryDate
      }
    }
  }
`;
