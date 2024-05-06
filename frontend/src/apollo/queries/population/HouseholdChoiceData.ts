import { gql } from '@apollo/client';

export const HouseholdChoiceData = gql`
  query householdChoiceData {
    residenceStatusChoices {
      name
      value
    }
    relationshipChoices {
      name
      value
    }
    roleChoices {
      name
      value
    }
    maritalStatusChoices {
      name
      value
    }
    workStatusChoices {
      name
      value
    }
    deduplicationBatchStatusChoices {
      name
      value
    }
    deduplicationGoldenRecordStatusChoices {
      name
      value
    }
    observedDisabilityChoices {
      name
      value
    }
    severityOfDisabilityChoices {
      name
      value
    }
    householdSearchTypesChoices {
      name
      value
    }
  }
`;
