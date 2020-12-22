import { gql } from 'apollo-boost';

export const householdMinimal = gql`
  fragment householdMinimal on HouseholdNode {
    id
    createdAt
    residenceStatus
    size
    totalCashReceived
    firstRegistrationDate
    lastRegistrationDate
    status
    sanctionListPossibleMatch
    hasDuplicates
    unicefId
    geopoint
    village
    adminArea {
      id
      title
      adminAreaType {
        adminLevel
      }
    }
    headOfHousehold {
      id
      fullName
    }
    address
    individuals {
      totalCount
    }
    programs {
      edges {
        node {
          id
          name
        }
      }
    }
  }
`;

export const householdDetailed = gql`
  fragment householdDetailed on HouseholdNode {
    ...householdMinimal
    countryOrigin
    country
    femaleAgeGroup05Count
    femaleAgeGroup611Count
    femaleAgeGroup1217Count
    femaleAdultsCount
    pregnantCount
    maleAgeGroup05Count
    maleAgeGroup611Count
    maleAgeGroup1217Count
    maleAdultsCount
    femaleAgeGroup05DisabledCount
    femaleAgeGroup611DisabledCount
    femaleAgeGroup1217DisabledCount
    femaleAdultsDisabledCount
    maleAgeGroup05DisabledCount
    maleAgeGroup611DisabledCount
    maleAgeGroup1217DisabledCount
    maleAdultsDisabledCount
    fchildHoh
    childHoh
    start
    end
    deviceid
    orgNameEnumerator
    returnee
    address
    nameEnumerator
    lastSyncAt
    consentSharing
    orgEnumerator
    updatedAt
    consent
    individuals {
      totalCount
      edges {
        node {
          ...individualMinimal
          birthDate
          relationship
          identities {
            id
            number
            type
          }
        }
      }
    }
    programs {
      edges {
        node {
          id
          name
        }
      }
    }
    registrationDataImport {
      name
      dataSource
      importDate
      importedBy {
        firstName
        lastName
        email
        username
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
