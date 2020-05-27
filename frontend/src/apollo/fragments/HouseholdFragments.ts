import { gql } from 'apollo-boost';

export const householdMinimal = gql`
  fragment householdMinimal on HouseholdNode {
    id
    createdAt
    residenceStatus
    size
    totalCashReceived
    registrationDate
    headOfHousehold {
      id
      fullName
    }
    address
    adminArea {
      id
      title
    }
    individuals {
      totalCount
    }
  }
`;

export const householdDetailed = gql`
  fragment householdDetailed on HouseholdNode {
    ...householdMinimal
    countryOrigin
    individuals {
      totalCount
      edges {
        node {
          ...individualMinimal
          birthDate
          relationship
        }
      }
    }
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
          fullName
          cashPlan {
            id
            totalPersonsCovered
            program {
              id
              name
            }
            totalDeliveredQuantity
            assistanceMeasurement
          }
        }
      }
    }
    flexFields
  }
`;
