import { gql } from '@apollo/client';

export const paymentRecordDetails = gql`
  fragment paymentRecordDetails on PaymentRecordNode {
    id
    status
    statusDate
    caId
    caHashId
    registrationCaId
    verification {
      id
      status
      statusDate
      receivedAmount
    }
    household {
      id
      status
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
    deliveryType {
        name
    }
    entitlementCardIssueDate
    entitlementCardNumber
    transactionReferenceId
    serviceProvider {
      id
      fullName
      shortName
    }
  }
`;
