import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_QUERY = gql`
  query PaymentRecord($id: ID!) {
    paymentRecord(id: $id) {
      id
      status
      statusDate
      caId
      caHashId
      registrationCaId
      fullName
      distributionModality
      totalPersonsCovered
      targetPopulation {
        id
        name
      }
      verification {
        id
        status
        statusDate
        receivedAmount
        isManuallyEditable
      }
      currency
      entitlementQuantity
      deliveredQuantity
      deliveryDate
      entitlementCardIssueDate
      entitlementCardNumber
      household {
        id
        size
        status
        unicefId
        headOfHousehold {
          id
          phoneNo
          phoneNoAlternative
          phoneNoValid
          phoneNoAlternativeValid
        }
      }
      parent {
        id
        caId
        program {
          id
          name
        }
        verificationPlans {
          edges {
            node {
              id
              status
              verificationChannel
            }
          }
        }
      }
      deliveredQuantityUsd
      deliveryType
      transactionReferenceId
      serviceProvider {
        id
        fullName
        shortName
      }
    }
  }
`;
