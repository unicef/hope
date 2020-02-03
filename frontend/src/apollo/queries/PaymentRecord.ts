import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_QUERY = gql`
  query PaymentRecord($id: ID!) {
    paymentRecord(id: $id) {
      id
      status
      statusDate
      cashAssistId
      household {
        householdCaId
        familySize
      }
      headOfHousehold
      distributionModality
      totalPersonCovered
      targetPopulation {
        name
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
