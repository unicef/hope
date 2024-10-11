import { gql } from '@apollo/client';

export const MARK_PAYMENT_AS_FAILED = gql`
  mutation markPayAsFailed($paymentId: ID!) {
    markPaymentAsFailed(paymentId: $paymentId) {
      payment {
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
