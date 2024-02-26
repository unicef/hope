import { gql } from '@apollo/client';

export const UPDATE_PROGRAM_MUTATION = gql`
  mutation UpdateProgram($programData: UpdateProgramInput!, $version: BigInt!) {
    updateProgram(programData: $programData, version: $version) {
      program {
        id
        name
        startDate
        endDate
        status
        caId
        description
        budget
        frequencyOfPayments
        cashPlus
        populationGoal
        scope
        sector
        totalNumberOfHouseholds
        administrativeAreasOfImplementation
        individualDataNeeded
        version
        dataCollectingType {
          id
          code
          label
          active
          individualFiltersAvailable
          householdFiltersAvailable
        }
      }
      validationErrors
    }
  }
`;
