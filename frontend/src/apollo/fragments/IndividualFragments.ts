import { gql } from 'apollo-boost';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    lastRegistrationDate
    createdAt
    updatedAt
    fullName
    sex
    unicefId
    birthDate
    maritalStatus
    phoneNo
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
          documentNumber
          type {
            country
            label
          }
        }
      }
    }
    identities {
      id
      agency {
        country
        label
      }
      number
    }

    household {
      id
      unicefId
      status
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
    hearingDisability
    observedDisability
    individualId
    seeingDisability
    physicalDisability
    selfcareDisability
    photo
    workStatus
    documents {
      edges {
        node {
          id
          type {
            country
            label
          }
          documentNumber
        }
      }
    }
    identities {
      id
      agency {
        country
        label
      }
      number
    }
    enrolledInNutritionProgramme
    administrationOfRutf
    identities {
      number
      type
      country
    }
    household {
      status
      id
      address
      countryOrigin
      adminArea {
        id
        title
        level
      }
    }
    role
    relationship
    headingHousehold {
      id
      headOfHousehold {
        id
      }
    }
    flexFields
  }
`;
