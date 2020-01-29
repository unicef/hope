import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_QUERY = gql`
  query PaymentRecord($id: ID!) {
    paymentRecord(id: $id) {
      id
      startDate
      cashAssistId
      deliveryType
      household {
        householdCaId
        familySize
      }
    }
  }
`;
