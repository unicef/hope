import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_QUERY = gql`
  query PaymentRecord($id: ID!) {
    paymentRecord(id: $id) {
      id
      status
      statusDate
      cashAssistId
      household {
        id
        size
      }
      headOfHousehold
      distributionModality
      totalPersonCovered
      targetPopulation {
        id
        name
      }
      cashPlan {
        id
        cashAssistId
        program {
          id
          name
        }
      }
      entitlement {
        id
        currency
        entitlementQuantity
        deliveredQuantity
        deliveryType
        deliveryDate
        entitlementCardIssueDate
        transactionReferenceId
        fsp
        entitlementCardNumber
      }
    }
  }
`;
