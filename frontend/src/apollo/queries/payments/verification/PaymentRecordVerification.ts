import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_VERIFICATION_QUERY = gql`
  query PaymentRecordVerification($id: ID!) {
    paymentRecordVerification(id: $id) {
      id
      status
      statusDate
      receivedAmount
      isManuallyEditable
      paymentRecord {
        id
        status
        statusDate
        caId
        caHashId
        registrationCaId
        household {
          status
          unicefId
          id
          size
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
        cashPlan {
          id
          caId
          program {
            id
            name
          }
          verifications {
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
      cashPlanPaymentVerification {
        id
        verificationChannel
      }
    }
  }
`;
