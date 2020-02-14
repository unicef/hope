import { gql } from 'apollo-boost';

export const HOUSEHOLD_QUERY = gql`
  query Household($id: ID!) {
    household(id: $id) {
      id
      createdAt
      familySize
      nationality
      location {
        id
        title
      }
      residenceStatus
      paymentRecords {
        edges {
          node {
            id
            headOfHousehold
            cashPlan {
              id
              program {
                id
                name
              }
              totalDeliveredQuantity
              currency
            }
          }
        }
      }
    }
  }
`;
