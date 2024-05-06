import { gql } from '@apollo/client';

export const Payment = gql`
  query Payment($id: ID!) {
    payment(id: $id) {
      id
      unicefId
      distributionModality
      status
      statusDate
      snapshotCollectorBankName
      snapshotCollectorBankAccountNumber
      debitCardNumber
      debitCardIssuer
      targetPopulation {
        id
        name
      }
      sourcePayment {
        id
        unicefId
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
          fullName
        }
      }
      collector {
        id
        unicefId
        fullName
        email
        phoneNo
        phoneNoValid
        phoneNoAlternative
        phoneNoAlternativeValid
      }
      parent {
        id
        status
        isFollowUp
        unicefId
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
      }
      additionalCollectorName
      additionalDocumentType
      additionalDocumentNumber
      reasonForUnsuccessfulPayment
      snapshotCollectorFullName
      adminUrl
    }
  }
`;
