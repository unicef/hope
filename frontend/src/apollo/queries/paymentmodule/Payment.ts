import { gql } from 'apollo-boost';

export const Payment = gql`
  query Payment($id: ID!) {
    payment(id: $id) {
      id
      unicefId
      distributionModality
      status
      statusDate
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
        phoneNo
        phoneNoValid
        phoneNoAlternative
        phoneNoAlternativeValid
      }
      parent {
        id
        status
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
    }
  }
`;
