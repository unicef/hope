import { gql } from 'apollo-boost';

export const householdMinimal = gql`
  fragment householdMinimal on HouseholdNode {
    id
    createdAt
    residenceStatus
    size
    totalCashReceived
    currency
    firstRegistrationDate
    lastRegistrationDate
    status
    sanctionListPossibleMatch
    sanctionListConfirmedMatch
    hasDuplicates
    unicefId
    flexFields
    unhcrId
    geopoint
    village
    admin1 {
      id
      title
      level
      pCode
    }
    admin2 {
      id
      title
      level
      pCode
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
    femaleAgeGroup04Count
    femaleAgeGroup512Count
    femaleAgeGroup1317Count
    femaleAgeGroup1859Count
    femaleAgeGroup60Count
    pregnantCount
    maleAgeGroup04Count
    maleAgeGroup512Count
    maleAgeGroup1317Count
    maleAgeGroup1859Count
    maleAgeGroup60Count
    femaleAgeGroup04DisabledCount
    femaleAgeGroup512DisabledCount
    femaleAgeGroup1317DisabledCount
    femaleAgeGroup1859DisabledCount
    femaleAgeGroup60DisabledCount
    maleAgeGroup04DisabledCount
    maleAgeGroup512DisabledCount
    maleAgeGroup1317DisabledCount
    maleAgeGroup1859DisabledCount
    maleAgeGroup60DisabledCount
    fchildHoh
    childHoh
    start
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
    programsWithDeliveredQuantity {
      id
      name
      quantity {
        totalDeliveredQuantity
        totalDeliveredQuantityUsd
        currency
      }
    }
  }
`;
