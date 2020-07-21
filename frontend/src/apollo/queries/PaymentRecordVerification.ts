import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_VERIFICATION_QUERY = gql`
  query PaymentRecordVerification($id: ID!) {
    paymentRecordVerification(id: $id) {
      id
      status
      statusDate
      receivedAmount
      paymentRecord {
        id
        status
        statusDate
        caId
        household {
          id
          size
          headOfHousehold {
            id
            phoneNo
            phoneNoAlternative
          }
        }
        fullName
        distributionModality
        totalPersonsCovered
        targetPopulation {
          id
          name
        }
        cashPlan {
          id
          caId
          program {
            id
            name
          }
        }
        currency
        entitlementQuantity
        deliveredQuantity
        deliveryDate
        deliveryDate
        deliveryType
        entitlementCardIssueDate
        entitlementCardNumber
        serviceProvider {
          id
          fullName
          shortName
        }
      }
    }
  }
`;
