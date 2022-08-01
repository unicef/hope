import { gql } from 'apollo-boost';

export const PAYMENT_QUERY = gql`
  query Payment($id: ID!) {
    payment(id: $id) {
      id
      household {
        id
        size
        admin2 {
          name
        }
      }
      status
      currency
      entitlementDate
      entitlementQuantityUsd
    }
  }
`;
