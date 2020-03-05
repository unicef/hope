import { gql } from 'apollo-boost';

export const HOUSEHOLD_QUERY = gql`
  query Household($id: ID!) {
    household(id: $id) {
      id
      createdAt
      familySize
      nationality
      totalCashReceived
      headOfHousehold {
        id
        fullName
      }
      individuals {
        totalCount
        edges {
          node {
            id
            individualCaId
            fullName
            sex
            dob
            nationality
            identificationType
            workStatus
            representedHouseholds {
              edges {
                node {
                  id
                  representative {
                    fullName
                  }
                }
              }
            }
          }
        }
      }
      location {
        id
        title
      }
      residenceStatus
      programs {
        edges {
          node {
            name
          }
        }
      }
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
