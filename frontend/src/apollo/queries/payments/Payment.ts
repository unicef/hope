import { gql } from 'apollo-boost';

export const Payment = gql`
  query Payment($id: ID!) {
    payment(id: $id) {
      id
      household {
        id
        unicefId
        size
        admin2 {
          id
          name
        }
      }
      entitlementQuantityUsd
    }
  }
`;
