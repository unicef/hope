import { gql } from '@apollo/client';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    age
    lastRegistrationDate
    rdiMergeStatus
    adminUrl
    createdAt
    updatedAt
    fullName
    sex
    unicefId
    birthDate
    maritalStatus
    phoneNo
    phoneNoValid
    email
    sanctionListPossibleMatch
    sanctionListConfirmedMatch
    deduplicationGoldenRecordStatus
    sanctionListLastCheck
    role
    relationship
    status
    documents {
      edges {
        node {
          id
          country
          countryIso3
          documentNumber
          photo
          type {
            label
            key
          }
        }
      }
    }
    identities {
      edges {
        node {
          id
          partner
          country
          number
        }
      }
    }
    household {
      id
      unicefId
      status
      importId
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
      program {
        id
        name
      }
      totalCashReceivedUsd
      lastRegistrationDate
      start
      firstRegistrationDate
      countryOrigin
      village
    }
  }
`;

export const individualDetailed = gql`
  fragment individualDetailed on IndividualNode {
    ...individualMinimal
    givenName
    familyName
    estimatedBirthDate
    pregnant
    lastSyncAt
    deduplicationBatchStatus
    disability
    commsDisability
    firstRegistrationDate
    whoAnswersAltPhone
    memoryDisability
    middleName
    whoAnswersPhone
    phoneNoAlternative
    phoneNoAlternativeValid
    email
    hearingDisability
    observedDisability
    individualId
    seeingDisability
    physicalDisability
    selfcareDisability
    disability
    photo
    workStatus
    accounts {
      id
      name
      dataFields
    }
    documents {
      edges {
        node {
          id
          country
          photo
          type {
            label
            key
          }
          documentNumber
        }
      }
    }
    enrolledInNutritionProgramme
    household {
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
      status
      id
      residenceStatus
      address
      village
      zipCode
      geopoint
      country
      countryOrigin
      deliveredQuantities {
        totalDeliveredQuantity
        currency
      }
      adminArea {
        id
        name
        level
      }
    }
    headingHousehold {
      id
      headOfHousehold {
        id
        givenName
        familyName
        fullName
      }
    }
    flexFields
    householdsAndRoles {
      id
      role
      household {
        id
        unicefId
      }
    }
    preferredLanguage
    paymentDeliveryPhoneNo
    walletName
    walletAddress
    blockchainName
    registrationDataImport {
      id
      name
    }
    importId
  }
`;

export const mergedIndividualMinimal = gql`
  fragment mergedIndividualMinimal on IndividualNode {
    id
    unicefId
    age
    fullName
    birthDate
    sex
    role
    relationship
    deduplicationBatchStatus
    deduplicationGoldenRecordStatus
    deduplicationGoldenRecordResults {
      hitId
      fullName
      score
      proximityToScore
      age
      location
    }
    deduplicationBatchResults {
      hitId
      fullName
      score
      proximityToScore
      age
      location
    }
    registrationDataImport {
      id
      name
    }
    importId
  }
`;
