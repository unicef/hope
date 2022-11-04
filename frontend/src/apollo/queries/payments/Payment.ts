import { gql } from 'apollo-boost';

export const Payment = gql`
query Payment($id: ID!) {
  payment(id: $id) {
    id
    unicefId
    status
    statusDate
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
      }
    }
    parent {
      id
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
  }
}
`;
