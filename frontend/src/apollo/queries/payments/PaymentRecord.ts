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
      household {
        id
        status
        size
      }
      fullName
      distributionModality
      totalPersonsCovered
      targetPopulation {
        id
        name
      }
      parent {
        id
        caId
        program {
          id
          name
        }
      }
      verification {
        id
        status
        statusDate
        receivedAmount
      }
      currency
      entitlementQuantity
      deliveredQuantity
      deliveryDate
      deliveryDate
      entitlementCardIssueDate
      entitlementCardNumber

      serviceProvider {
        id
        fullName
        shortName
      }

      id
      status
      statusDate
      caId
      household {
        id
        size
        unicefId
        headOfHousehold {
          id
          phoneNo
          phoneNoAlternative
          phoneNoValid
          phoneNoAlternativeValid
        }
      }
      fullName
      distributionModality
      totalPersonsCovered
      targetPopulation {
        id
        name
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
      currency
      entitlementQuantity
      deliveredQuantity
      deliveredQuantityUsd
      deliveryDate
      deliveryDate
      deliveryType
      entitlementCardIssueDate
      entitlementCardNumber
      transactionReferenceId
      serviceProvider {
        id
        fullName
        shortName
      }
    }
  }
`;
