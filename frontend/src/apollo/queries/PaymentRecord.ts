import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_QUERY = gql`
  query PaymentRecord($id: ID!) {
    paymentRecord(id: $id) {
      id
      status
      statusDate
      caId
      household {
        id
        size
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
      verifications {
        totalCount
        edges {
          node {
            id
            status
            statusDate
            receivedAmount
          }
        }
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
              verificationMethod
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
      serviceProvider {
        id
        fullName
        shortName
      }
    }
  }
`;
