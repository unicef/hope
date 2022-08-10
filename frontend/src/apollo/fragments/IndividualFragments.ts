import { gql } from 'apollo-boost';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    age
    lastRegistrationDate
    createdAt
    updatedAt
    fullName
    sex
    unicefId
    birthDate
    maritalStatus
    phoneNo
    phoneNoValid
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
          documentNumber
          photo
          type {
            country
            label
            type
            countryIso3
          }
        }
      }
    }
    identities {
      edges {
        node {
          id
          agency {
            country
            label
            countryIso3
          }
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
    status
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
    hearingDisability
    observedDisability
    individualId
    seeingDisability
    physicalDisability
    selfcareDisability
    disability
    photo
    workStatus
    documents {
      edges {
        node {
          id
          country
          photo
          type {
            country
            label
          }
          documentNumber
        }
      }
    }
    identities {
      edges {
        node {
          id
          agency {
            country
            label
          }
          number
        }
      }
    }
    enrolledInNutritionProgramme
    administrationOfRutf
    identities {
      edges {
        node {
          id
          number
          type
          country
        }
      }
    }
    household {
      status
      id
      address
      countryOrigin
      adminArea {
        id
        name
        level
      }
    }
    role
    relationship
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
    }
  }
`;
