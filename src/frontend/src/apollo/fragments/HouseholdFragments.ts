import { gql } from '@apollo/client';

export const householdMinimal = gql`
  fragment householdMinimal on HouseholdNode {
    id
    status
    adminUrl
    createdAt
    residenceStatus
    maleChildrenCount
    femaleChildrenCount
    childrenDisabledCount
    size
    totalCashReceived
    totalCashReceivedUsd
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
    adminAreaTitle
    admin1 {
      id
      name
      level
      pCode
    }
    admin2 {
      id
      name
      level
      pCode
    }
    admin3 {
      id
      name
      level
      pCode
    }
    admin4 {
      id
      name
      level
      pCode
    }
    headOfHousehold {
      id
      fullName
      givenName
      familyName
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
    activeIndividualsCount
    countryOrigin
    country
    zipCode
    femaleAgeGroup05Count
    femaleAgeGroup611Count
    femaleAgeGroup1217Count
    femaleAgeGroup1859Count
    femaleAgeGroup60Count
    pregnantCount
    maleAgeGroup05Count
    maleAgeGroup611Count
    maleAgeGroup1217Count
    maleAgeGroup1859Count
    maleAgeGroup60Count
    femaleAgeGroup05DisabledCount
    femaleAgeGroup611DisabledCount
    femaleAgeGroup1217DisabledCount
    femaleAgeGroup1859DisabledCount
    femaleAgeGroup60DisabledCount
    maleAgeGroup05DisabledCount
    maleAgeGroup611DisabledCount
    maleAgeGroup1217DisabledCount
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
    collectIndividualData
    individuals {
      totalCount
      edges {
        node {
          ...individualMinimal
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
    paymentrecordSet {
      edges {
        node {
          id
          fullName
          parent {
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
    deliveredQuantities {
      totalDeliveredQuantity
      currency
    }
    programRegistrationId
  }
`;

export const mergedHouseholdMinimal = gql`
  fragment mergedHouseholdMinimal on HouseholdNode {
    id
    unicefId
    headOfHousehold {
      id
      fullName
    }
    size
    admin1 {
      id
      name
    }
    admin2 {
      id
      name
    }
    firstRegistrationDate
    hasDuplicates
  }
`;
