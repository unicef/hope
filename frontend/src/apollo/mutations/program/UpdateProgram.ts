import { gql } from '@apollo/client';

export const UPDATE_PROGRAM_MUTATION = gql`
  mutation UpdateProgram($programData: UpdateProgramInput!, $version: BigInt!) {
    updateProgram(programData: $programData, version: $version) {
      program {
        id
        name
        programmeCode
        startDate
        endDate
        status
        caId
        caHashId
        description
        budget
        frequencyOfPayments
        cashPlus
        populationGoal
        scope
        sector
        totalNumberOfHouseholds
        totalNumberOfHouseholdsWithTpInProgram
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
          description
        }
        partners {
          id
          name
          areaAccess
          adminAreas
        }
      }
      validationErrors
    }
  }
`;
