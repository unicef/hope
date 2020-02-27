import { gql } from 'apollo-boost';

export const HOUSEHOLD_QUERY = gql`
  query Household($id: ID!) {
    household(id: $id) {
      id
      createdAt
      familySize
      nationality
      individuals {
        edges {
          node {
            id
            individualCaId
            fullName
            sex
            dob
            nationality
            identificationType
          }
        }
      }
      location {
        id
        title
      }
      individuals {
        totalCount
      }
      residenceStatus
      paymentRecords {
        edges {
          node {
            id
            headOfHousehold
            cashPlan {
              id
              numberOfHouseholds
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
