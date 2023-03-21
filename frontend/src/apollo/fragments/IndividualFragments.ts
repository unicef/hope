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
          countryIso3
          documentNumber
          photo
          type {
            label
            type
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
            label
          }
          documentNumber
        }
      }
    }
    enrolledInNutritionProgramme
    administrationOfRutf
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
    preferredLanguage
  }
`;
