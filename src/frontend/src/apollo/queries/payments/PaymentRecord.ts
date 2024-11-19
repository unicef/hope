import { gql } from '@apollo/client';

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
        adminUrl
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
          unicefId
          phoneNo
          phoneNoAlternative
          phoneNoValid
          phoneNoAlternativeValid
          fullName
        }
      }
      parent {
        id
        unicefId
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
      deliveryType {
          name
      }
      transactionReferenceId
      serviceProvider {
        id
        fullName
        shortName
      }
    }
  }
`;
