import { gql } from 'apollo-boost';

export const REVERT_MARK_PAYMENT_AS_FAILED = gql`
  mutation revertMarkPaymentAsFailed(
    $paymentId: ID!
    $deliveredQuantity: Decimal!
    $deliveryDate: Date!
  ) {
    revertMarkPaymentAsFailed(
      paymentId: $paymentId
      deliveredQuantity: $deliveredQuantity
      deliveryDate: $deliveryDate
    ) {
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
  }
`;
