import { gql } from '@apollo/client';

export const registrationMinimal = gql`
  fragment registrationMinimal on RegistrationDataImportNode {
    id
    createdAt
    name
    status
    erased
    importDate
    importedBy {
      id
      firstName
      lastName
      email
    }
    dataSource
    numberOfHouseholds
    numberOfIndividuals
    program {
      id
      name
      startDate
      endDate
      status
    }
    refuseReason
    totalHouseholdsCountWithValidPhoneNo
    adminUrl
    biometricDeduplicated
  }
`;

export const registrationDetailed = gql`
  fragment registrationDetailed on RegistrationDataImportNode {
    ...registrationMinimal
    numberOfIndividuals
    datahubId
    errorMessage
    batchDuplicatesCountAndPercentage {
      count
      percentage
    }
    batchUniqueCountAndPercentage {
      count
      percentage
    }
    goldenRecordUniqueCountAndPercentage {
      count
      percentage
    }
    goldenRecordDuplicatesCountAndPercentage {
      count
      percentage
    }
    goldenRecordPossibleDuplicatesCountAndPercentage {
      count
      percentage
    }
    canMerge
    biometricDeduplicationEnabled
    deduplicationEngineStatus
  }
`;

export const importedHouseholdMinimal = gql`
  fragment importedHouseholdMinimal on ImportedHouseholdNode {
    id
    importId
    headOfHousehold {
      id
      fullName
    }
    size
    admin1 {
      pCode
      name
    }
    admin2 {
      pCode
      name
    }
    flexFields
    deviceid
    start
    detailId
    firstRegistrationDate
    lastRegistrationDate
    hasDuplicates
    fchildHoh
    childHoh
    collectIndividualData
  }
`;
export const importedHouseholdDetailed = gql`
  fragment importedHouseholdDetailed on ImportedHouseholdNode {
    ...importedHouseholdMinimal
    residenceStatus
    country
    countryOrigin
    registrationDataImport {
      id
      name
    }
    individuals {
      edges {
        node {
          ...importedIndividualMinimal
        }
      }
    }
  }
`;

export const importedIndividualMinimal = gql`
  fragment importedIndividualMinimal on ImportedIndividualNode {
    id
    importId
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
    }
  }
`;

export const importedIndividualDetailed = gql`
  fragment importedIndividualDetailed on ImportedIndividualNode {
    ...importedIndividualMinimal
    photo
    givenName
    familyName
    middleName
    estimatedBirthDate
    maritalStatus
    workStatus
    pregnant
    flexFields
    importId
    observedDisability
    seeingDisability
    hearingDisability
    physicalDisability
    memoryDisability
    selfcareDisability
    commsDisability
    disability
    documents {
      edges {
        node {
          id
          country
          type {
            label
            key
          }
          documentNumber
          photo
        }
      }
    }
    identities {
      edges {
        node {
          id
          number
          partner
          country
        }
      }
    }
    role
    relationship
    household {
      id
      importId
      admin1 {
        pCode
        name
      }
      admin2 {
        pCode
        name
      }
      address
    }
    registrationDataImport {
      id
      name
    }
    phoneNo
    phoneNoAlternative
    phoneNoValid
    phoneNoAlternativeValid
    preferredLanguage
    email
  }
`;
