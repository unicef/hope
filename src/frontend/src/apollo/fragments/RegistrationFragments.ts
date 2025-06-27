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
