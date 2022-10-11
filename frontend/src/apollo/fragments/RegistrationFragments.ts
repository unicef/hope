import { gql } from 'apollo-boost';

export const registrationMinimal = gql`
  fragment registrationMinimal on RegistrationDataImportNode {
    id
    createdAt
    name
    status
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
    batchPossibleDuplicatesCountAndPercentage {
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
    admin1
    admin1Title
    admin2
    admin2Title
    flexFields
    deviceid
    start
    koboAssetId
    rowId
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
      hctId
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
      hctId
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
            country
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
          documentNumber
          type
          country
        }
      }
    }
    role
    relationship
    household {
      id
      importId
      admin1
      admin2
      address
    }
    registrationDataImport {
      id
      hctId
      name
    }
    phoneNo
    phoneNoAlternative
    phoneNoValid
    phoneNoAlternativeValid
  }
`;
