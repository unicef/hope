import { gql } from 'apollo-boost';

export const REVERT_MARK_PAYMENT_AS_FAILED = gql`
  mutation revertMarkPayAsFailed(
    $paymentId: ID!
    $deliveredQuantity: Decimal!
    $deliveryDate: Date!
  ) {
    revertMarkPaymentAsFailed(
      paymentId: $paymentId
      deliveredQuantity: $deliveredQuantity
      deliveryDate: $deliveryDate
    ) {
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
