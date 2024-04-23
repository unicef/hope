import { gql } from '@apollo/client';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    age
    lastRegistrationDate
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
      programs {
        edges {
          node {
            id
            name
          }
        }
      }
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
    importedIndividualId
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
    paymentChannels {
      id
      bankName
      bankAccountNumber
      accountHolderName
      bankBranchName
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
    administrationOfRutf
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
    bankAccountInfo {
      bankName
      bankAccountNumber
      accountHolderName
      bankBranchName
    }
    preferredLanguage
    paymentDeliveryPhoneNo
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
      datahubId
    }
  }
`;
