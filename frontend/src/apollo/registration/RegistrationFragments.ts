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
    headOfHousehold {
      id
      fullName
    }
    size
    admin1
    admin2
    firstRegistrationDate
    lastRegistrationDate
    hasDuplicates
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
  }
`;

export const importedIndividualMinimal = gql`
  fragment importedIndividualMinimal on ImportedIndividualNode {
    id
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
    }
    deduplicationBatchResults {
      hitId
      fullName
      score
      proximityToScore
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
    givenName
    familyName
    middleName
    estimatedBirthDate
    maritalStatus
    documents {
      edges {
        node {
          id
          type {
            label
          }
          documentNumber
        }
      }
    }
    identities {
      id
      documentNumber
      type
    }
    role
    relationship
    household {
      id
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
  }
`;
